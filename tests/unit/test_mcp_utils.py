"""Unit tests for ``fmp_data.mcp.utils``.

Two things are pinned here.

The first is FMP-SEC-001: a manifest is *data*. ``load_manifest_tools``
parses a Python manifest with a restricted AST walk that accepts a
docstring and a single module-level ``TOOLS = ["..."]`` assignment and
nothing else. Every refusal case in ``REFUSAL_SOURCES`` is a manifest that
would write a marker file if it were ever imported or ``exec``'d, so each
case asserts both the refusal *and* the absence of the side effect. A
regression that reintroduced ``exec``/``import`` would still raise for some
of these shapes while silently running their payload -- the marker file is
what makes that distinguishable from a genuine refusal.

The second is the setup helper surface (config path, config load/save,
interpreter discovery, subprocess-backed server start, in-process API-key
probe). Those functions decide where the tool writes and what it reports
back to the user, so they are tested through fakes for the OS-facing
collaborators only -- ``platform``, ``os.environ``, ``subprocess.run``,
``FMPDataClient``, ``Path.exists`` -- never by faking the function under
test. Helper return values are classified reasons, never stderr.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any, ClassVar

import pytest

from fmp_data.mcp import utils as mcp_utils

POSIX_ONLY = pytest.mark.skipif(os.name == "nt", reason="POSIX mode bits")
#: ``os.geteuid`` is absent on Windows and skipif conditions are evaluated at
#: import time, so a bare call would break collection there even under
#: ``POSIX_ONLY``.
NOT_ROOT = pytest.mark.skipif(
    getattr(os, "geteuid", lambda: 1)() == 0,
    reason="root ignores file permissions",
)


def _mode(path: Path) -> int:
    return path.stat().st_mode & 0o777


def _write_manifest(tmp_path: Path, name: str, source: str) -> Path:
    path = tmp_path / name
    path.write_text(source, encoding="utf-8")
    return path


class _FakeRun:
    """Stand-in for ``subprocess.run`` that records how it was called."""

    def __init__(
        self,
        returncode: int = 0,
        stdout: str = "",
        stderr: str = "",
        raises: BaseException | None = None,
    ) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.raises = raises
        self.calls: list[tuple[list[str], dict[str, Any]]] = []

    def __call__(
        self, cmd: list[str], **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        self.calls.append((cmd, kwargs))
        if self.raises is not None:
            raise self.raises
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=self.returncode,
            stdout=self.stdout,
            stderr=self.stderr,
        )


# ---------------------------------------------------------------------------
# get_claude_config_path
# ---------------------------------------------------------------------------


class TestGetClaudeConfigPath:
    def test_macos_path_is_under_application_support(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr(platform, "system", lambda: "Darwin")
        monkeypatch.setenv("HOME", str(tmp_path))

        assert mcp_utils.get_claude_config_path() == (
            tmp_path
            / "Library"
            / "Application Support"
            / "Claude"
            / "claude_desktop_config.json"
        )

    def test_windows_path_is_under_appdata(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr(platform, "system", lambda: "Windows")
        monkeypatch.setenv("APPDATA", str(tmp_path / "AppData"))

        assert mcp_utils.get_claude_config_path() == (
            tmp_path / "AppData" / "Claude" / "claude_desktop_config.json"
        )

    def test_windows_without_appdata_yields_a_relative_path(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Current behaviour: an unset APPDATA degrades to a CWD-relative path."""
        monkeypatch.setattr(platform, "system", lambda: "Windows")
        monkeypatch.delenv("APPDATA", raising=False)

        result = mcp_utils.get_claude_config_path()

        assert result == Path("Claude") / "claude_desktop_config.json"
        assert not result.is_absolute()

    def test_linux_path_is_under_dot_config(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        monkeypatch.setenv("HOME", str(tmp_path))

        assert mcp_utils.get_claude_config_path() == (
            tmp_path / ".config" / "Claude" / "claude_desktop_config.json"
        )


# ---------------------------------------------------------------------------
# find_python_executable
# ---------------------------------------------------------------------------


class TestFindPythonExecutable:
    def test_prefers_the_running_interpreter_without_probing(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        interpreter = tmp_path / "python3.13"
        interpreter.write_text("#!/bin/sh\n", encoding="utf-8")
        fake = _FakeRun()
        monkeypatch.setattr(sys, "executable", str(interpreter))
        monkeypatch.setattr(subprocess, "run", fake)

        assert mcp_utils.find_python_executable() == str(interpreter)
        assert fake.calls == []

    def test_falls_back_to_first_command_which_resolves(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "executable", "")
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        recorded: list[list[str]] = []

        def fake_run(cmd: list[str], **kwargs: Any) -> Any:
            recorded.append(cmd)
            if cmd[0] == "which":
                return subprocess.CompletedProcess(
                    cmd, 0, stdout="/usr/local/bin/python3\n/usr/bin/python3\n"
                )
            return subprocess.CompletedProcess(cmd, 0, stdout="Python 3.13.0\n")

        monkeypatch.setattr(subprocess, "run", fake_run)

        assert mcp_utils.find_python_executable() == "/usr/local/bin/python3"
        assert recorded == [["python3", "--version"], ["which", "python3"]]

    def test_skips_commands_that_are_not_installed(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "executable", "")
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        recorded: list[list[str]] = []

        def fake_run(cmd: list[str], **kwargs: Any) -> Any:
            recorded.append(cmd)
            if cmd[0] == "python3":
                raise FileNotFoundError(cmd[0])
            if cmd[0] == "which":
                return subprocess.CompletedProcess(cmd, 0, stdout="/opt/bin/python\n")
            return subprocess.CompletedProcess(cmd, 0, stdout="Python 3.12.0\n")

        monkeypatch.setattr(subprocess, "run", fake_run)

        assert mcp_utils.find_python_executable() == "/opt/bin/python"
        assert recorded[0] == ["python3", "--version"]
        assert ["which", "python"] in recorded

    def test_skips_commands_whose_version_probe_fails(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "executable", "")
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        recorded: list[list[str]] = []

        def fake_run(cmd: list[str], **kwargs: Any) -> Any:
            recorded.append(cmd)
            if cmd[0] == "python3":
                return subprocess.CompletedProcess(cmd, 127, stdout="")
            if cmd[0] == "which":
                return subprocess.CompletedProcess(cmd, 0, stdout="/opt/bin/python\n")
            return subprocess.CompletedProcess(cmd, 0, stdout="Python 3.12.0\n")

        monkeypatch.setattr(subprocess, "run", fake_run)

        assert mcp_utils.find_python_executable() == "/opt/bin/python"
        assert ["which", "python3"] not in recorded

    def test_uses_where_on_windows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "executable", "")
        monkeypatch.setattr(platform, "system", lambda: "Windows")
        recorded: list[list[str]] = []

        def fake_run(cmd: list[str], **kwargs: Any) -> Any:
            recorded.append(cmd)
            if cmd[0] == "where":
                return subprocess.CompletedProcess(
                    cmd, 0, stdout="C:\\Python\\python3.exe\n"
                )
            return subprocess.CompletedProcess(cmd, 0, stdout="Python 3.12.0\n")

        monkeypatch.setattr(subprocess, "run", fake_run)

        assert mcp_utils.find_python_executable() == "C:\\Python\\python3.exe"
        assert ["where", "python3"] in recorded
        assert not any(cmd[0] == "which" for cmd in recorded)

    def test_defaults_to_python3_when_no_probe_resolves(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "executable", "")
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        recorded: list[list[str]] = []

        def fake_run(cmd: list[str], **kwargs: Any) -> Any:
            recorded.append(cmd)
            if cmd[0] == "which":
                return subprocess.CompletedProcess(cmd, 1, stdout="")
            return subprocess.CompletedProcess(cmd, 0, stdout="Python 3.12.0\n")

        monkeypatch.setattr(subprocess, "run", fake_run)

        assert mcp_utils.find_python_executable() == "python3"
        # The candidate list and its order are the contract: a version probe
        # followed by a path resolution, most-preferred name first.
        assert recorded == [
            ["python3", "--version"],
            ["which", "python3"],
            ["python", "--version"],
            ["which", "python"],
            ["python3.10", "--version"],
            ["which", "python3.10"],
            ["python3.11", "--version"],
            ["which", "python3.11"],
            ["python3.12", "--version"],
            ["which", "python3.12"],
        ]

    def test_defaults_to_python3_when_every_probe_errors(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(sys, "executable", "")
        fake = _FakeRun(raises=subprocess.SubprocessError("no exec"))
        monkeypatch.setattr(subprocess, "run", fake)

        assert mcp_utils.find_python_executable() == "python3"
        # Every candidate is still tried; a raising probe skips only itself.
        assert [cmd for cmd, _ in fake.calls] == [
            ["python3", "--version"],
            ["python", "--version"],
            ["python3.10", "--version"],
            ["python3.11", "--version"],
            ["python3.12", "--version"],
        ]


# ---------------------------------------------------------------------------
# check_claude_desktop_installed
# ---------------------------------------------------------------------------


class TestCheckClaudeDesktopInstalled:
    @staticmethod
    def _only_these_exist(
        monkeypatch: pytest.MonkeyPatch, existing: set[str]
    ) -> list[str]:
        """Make only *existing* report as present; return the probe log."""
        probed: list[str] = []

        def fake_exists(self: Path) -> bool:
            probed.append(str(self))
            return str(self) in existing

        monkeypatch.setattr(Path, "exists", fake_exists)
        return probed

    def test_true_when_config_directory_exists(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "Claude" / "claude_desktop_config.json"
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)
        probed = self._only_these_exist(monkeypatch, {str(config.parent)})

        assert mcp_utils.check_claude_desktop_installed() is True
        # A present config dir short-circuits: no platform probe is needed.
        assert probed == [str(config.parent)]

    def test_true_on_macos_when_only_the_app_bundle_exists(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "Claude" / "claude_desktop_config.json"
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)
        monkeypatch.setattr(platform, "system", lambda: "Darwin")
        self._only_these_exist(monkeypatch, {"/Applications/Claude.app"})

        assert mcp_utils.check_claude_desktop_installed() is True

    def test_false_on_macos_without_config_dir_or_app_bundle(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "Claude" / "claude_desktop_config.json"
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)
        monkeypatch.setattr(platform, "system", lambda: "Darwin")
        self._only_these_exist(monkeypatch, set())

        assert mcp_utils.check_claude_desktop_installed() is False

    def test_true_on_windows_when_program_files_has_claude(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "Claude" / "claude_desktop_config.json"
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)
        monkeypatch.setattr(platform, "system", lambda: "Windows")
        monkeypatch.setenv("ProgramFiles", str(tmp_path / "PF"))
        self._only_these_exist(monkeypatch, {str(tmp_path / "PF" / "Claude")})

        assert mcp_utils.check_claude_desktop_installed() is True

    def test_windows_without_program_files_env_probes_the_documented_default(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """An unset ``ProgramFiles`` must fall back to ``C:\\Program Files``.

        The bare Program Files directory existing is deliberately *not*
        enough -- only a ``Claude`` subdirectory counts.
        """
        config = tmp_path / "Claude" / "claude_desktop_config.json"
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)
        monkeypatch.setattr(platform, "system", lambda: "Windows")
        monkeypatch.delenv("ProgramFiles", raising=False)
        probed = self._only_these_exist(monkeypatch, {"C:\\Program Files"})

        assert mcp_utils.check_claude_desktop_installed() is False
        assert probed == [
            str(config.parent),
            str(Path("C:\\Program Files") / "Claude"),
        ]

    def test_false_on_linux_without_config_dir(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "Claude" / "claude_desktop_config.json"
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        probed = self._only_these_exist(monkeypatch, {"/Applications/Claude.app"})

        assert mcp_utils.check_claude_desktop_installed() is False
        # Linux has no bundle fallback: the macOS app path is never consulted.
        assert probed == [str(config.parent)]


# ---------------------------------------------------------------------------
# load_claude_config / save_claude_config
# ---------------------------------------------------------------------------


class TestLoadClaudeConfig:
    def test_returns_parsed_object(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "claude_desktop_config.json"
        config.write_text('{"mcpServers": {"fmp": {"command": "py"}}}', "utf-8")
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)

        assert mcp_utils.load_claude_config() == {
            "mcpServers": {"fmp": {"command": "py"}}
        }

    def test_returns_empty_dict_when_file_is_absent(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "missing" / "claude_desktop_config.json"
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)

        assert mcp_utils.load_claude_config() == {}

    def test_rejects_a_json_array(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "claude_desktop_config.json"
        config.write_text('["not", "an", "object"]', "utf-8")
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)

        with pytest.raises(TypeError, match="must be an object"):
            mcp_utils.load_claude_config()

    def test_propagates_invalid_json(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "claude_desktop_config.json"
        config.write_text("{not json", "utf-8")
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)

        with pytest.raises(json.JSONDecodeError):
            mcp_utils.load_claude_config()


class TestSaveClaudeConfig:
    def test_writes_indented_json_with_trailing_newline(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "Claude" / "claude_desktop_config.json"
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)
        payload = {"mcpServers": {"fmp-data": {"args": ["-m", "fmp_data.mcp"]}}}

        backup = mcp_utils.save_claude_config(payload, backup=False)

        assert backup is None
        assert (
            config.read_text(encoding="utf-8") == json.dumps(payload, indent=2) + "\n"
        )

    def test_backup_keeps_the_previous_contents(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "Claude" / "claude_desktop_config.json"
        config.parent.mkdir()
        config.write_text('{"mcpServers": {"old": {}}}\n', encoding="utf-8")
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)

        backup = mcp_utils.save_claude_config({"mcpServers": {"new": {}}})

        assert backup is not None
        assert json.loads(backup.read_text()) == {"mcpServers": {"old": {}}}
        assert json.loads(config.read_text()) == {"mcpServers": {"new": {}}}
        assert backup.name.startswith("claude_desktop_config.backup_")

    def test_backup_is_skipped_when_no_config_exists_yet(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "Claude" / "claude_desktop_config.json"
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)

        backup = mcp_utils.save_claude_config({"a": 1}, backup=True)

        assert backup is None
        assert [p.name for p in config.parent.iterdir()] == [config.name]

    def test_unserialisable_payload_leaves_no_partial_file(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        config = tmp_path / "Claude" / "claude_desktop_config.json"
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)

        with pytest.raises(TypeError):
            mcp_utils.save_claude_config({"handle": object()}, backup=False)

        assert not config.exists()
        assert list(config.parent.iterdir()) == []

    def test_a_failed_write_does_not_truncate_the_previous_config(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """The temp-file-then-``os.replace`` path, stated as behaviour.

        A direct ``open(path, "w")`` implementation would empty the file
        before ``json.dump`` raised, so this is what makes the write atomic
        rather than merely tidy.
        """
        config = tmp_path / "Claude" / "claude_desktop_config.json"
        config.parent.mkdir()
        config.write_text('{"mcpServers": {"old": {}}}\n', encoding="utf-8")
        monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: config)

        with pytest.raises(TypeError):
            mcp_utils.save_claude_config({"handle": object()}, backup=False)

        assert json.loads(config.read_text()) == {"mcpServers": {"old": {}}}
        assert [p.name for p in config.parent.iterdir()] == [config.name]


class TestChmodUserOnly:
    @POSIX_ONLY
    def test_narrows_mode_to_owner_only(self, tmp_path: Path) -> None:
        target = tmp_path / "cfg.json"
        target.write_text("{}", encoding="utf-8")
        os.chmod(target, 0o644)

        mcp_utils._chmod_user_only(target, 0o600)

        assert _mode(target) == 0o600

    @POSIX_ONLY
    def test_is_a_no_op_on_windows(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        target = tmp_path / "cfg.json"
        target.write_text("{}", encoding="utf-8")
        os.chmod(target, 0o644)
        monkeypatch.setattr(os, "name", "nt")

        mcp_utils._chmod_user_only(target, 0o600)

        assert _mode(target) == 0o644

    @POSIX_ONLY
    def test_swallows_oserror_from_chmod(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        target = tmp_path / "cfg.json"
        target.write_text("{}", encoding="utf-8")
        os.chmod(target, 0o644)
        attempts: list[tuple[Any, int]] = []

        def boom(path: Any, mode: int, *args: Any, **kwargs: Any) -> None:
            attempts.append((path, mode))
            raise OSError("read-only filesystem")

        monkeypatch.setattr(os, "chmod", boom)

        mcp_utils._chmod_user_only(target, 0o600)  # must not propagate

        # Without this the test would also pass for an implementation that
        # never attempted the chmod at all.
        assert attempts == [(target, 0o600)]
        assert _mode(target) == 0o644


# ---------------------------------------------------------------------------
# add_mcp_server_to_config
# ---------------------------------------------------------------------------


class TestAddMcpServerToConfig:
    def test_creates_the_servers_section(self) -> None:
        config: dict[str, Any] = {}

        result = mcp_utils.add_mcp_server_to_config(
            config, "fmp-data", "/usr/bin/python3", "KEY123"
        )

        assert result is config
        assert result["mcpServers"]["fmp-data"] == {
            "command": "/usr/bin/python3",
            "args": ["-m", "fmp_data.mcp"],
            "env": {"FMP_API_KEY": "KEY123"},  # pragma: allowlist secret
        }

    def test_manifest_path_is_passed_through_the_environment(self) -> None:
        result = mcp_utils.add_mcp_server_to_config(
            {}, "fmp-data", "python3", "KEY123", manifest_path="/etc/tools.json"
        )

        assert result["mcpServers"]["fmp-data"]["env"] == {
            "FMP_API_KEY": "KEY123",  # pragma: allowlist secret
            "FMP_MCP_MANIFEST": "/etc/tools.json",
        }

    def test_omits_the_manifest_variable_when_not_given(self) -> None:
        result = mcp_utils.add_mcp_server_to_config({}, "fmp", "python3", "K")

        assert "FMP_MCP_MANIFEST" not in result["mcpServers"]["fmp"]["env"]

    def test_preserves_other_servers_and_replaces_its_own(self) -> None:
        config = {
            "mcpServers": {
                "other": {"command": "node"},
                "fmp-data": {
                    "command": "stale",
                    "env": {"FMP_API_KEY": "OLD"},  # pragma: allowlist secret
                },
            },
            "unrelated": True,
        }

        result = mcp_utils.add_mcp_server_to_config(
            config, "fmp-data", "python3", "NEW"
        )

        assert result["mcpServers"]["other"] == {"command": "node"}
        assert result["unrelated"] is True
        assert result["mcpServers"]["fmp-data"] == {
            "command": "python3",
            "args": ["-m", "fmp_data.mcp"],
            "env": {"FMP_API_KEY": "NEW"},  # pragma: allowlist secret
        }


# ---------------------------------------------------------------------------
# test_mcp_server (aliased: the source name would be collected by pytest)
# ---------------------------------------------------------------------------

run_mcp_server_check = mcp_utils.test_mcp_server


class TestRunMcpServerCheck:
    def test_reports_success_and_passes_the_key_by_environment(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("FMP_API_KEY", raising=False)
        monkeypatch.delenv("FMP_MCP_MANIFEST", raising=False)
        fake = _FakeRun(returncode=0, stdout="Server initialized successfully\n")
        monkeypatch.setattr(subprocess, "run", fake)

        assert run_mcp_server_check("KEY123") == (True, "passed")

        cmd, kwargs = fake.calls[0]
        assert cmd[0] == sys.executable
        # The probe has to actually build the app; a bare `print()` would
        # satisfy a test that only looked at the interpreter and the env.
        assert cmd[1] == "-c"
        assert "from fmp_data.mcp.server import create_app" in cmd[2]
        assert "create_app()" in cmd[2]
        assert kwargs["env"]["FMP_API_KEY"] == "KEY123"  # pragma: allowlist secret
        assert "FMP_MCP_MANIFEST" not in kwargs["env"]
        assert kwargs["timeout"] == 5
        # Output is captured so a key quoted on stderr never reaches the
        # caller; the return is a classified reason, not that text (#319).
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        assert "FMP_API_KEY" not in os.environ

    def test_forwards_the_manifest_path(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.delenv("FMP_MCP_MANIFEST", raising=False)
        fake = _FakeRun(returncode=0)
        monkeypatch.setattr(subprocess, "run", fake)
        manifest = str(tmp_path / "tools.yaml")

        assert run_mcp_server_check("KEY123", manifest_path=manifest) == (
            True,
            "passed",
        )

        env = fake.calls[0][1]["env"]
        assert env["FMP_MCP_MANIFEST"] == manifest
        assert env["FMP_API_KEY"] == "KEY123"  # pragma: allowlist secret
        assert "FMP_MCP_MANIFEST" not in os.environ

    def test_nonzero_exit_is_failed_without_stderr(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            subprocess,
            "run",
            _FakeRun(returncode=1, stderr="  ImportError: mcp apikey=KEY123  "),
        )

        assert run_mcp_server_check("KEY123") == (False, "failed")

    def test_reports_unknown_error_when_stderr_is_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(subprocess, "run", _FakeRun(returncode=2, stderr=""))

        assert run_mcp_server_check("KEY123") == (False, "failed")

    def test_timeout_counts_as_a_started_server(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            subprocess,
            "run",
            _FakeRun(raises=subprocess.TimeoutExpired(cmd="py", timeout=5)),
        )

        assert run_mcp_server_check("KEY123") == (True, "started")

    def test_unexpected_exception_is_reported_not_raised(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            subprocess, "run", _FakeRun(raises=OSError("no such executable"))
        )

        assert run_mcp_server_check("KEY123") == (False, "unavailable")


# ---------------------------------------------------------------------------
# get_api_key_from_env / validate_api_key
# ---------------------------------------------------------------------------


class TestGetApiKeyFromEnv:
    def test_returns_the_environment_value(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("FMP_API_KEY", "KEY123")

        assert mcp_utils.get_api_key_from_env() == "KEY123"

    def test_returns_none_when_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("FMP_API_KEY", raising=False)

        assert mcp_utils.get_api_key_from_env() is None


class _FakeCompany:
    def __init__(self, quote: Any = None, raises: BaseException | None = None) -> None:
        self.quote = quote
        self.raises = raises
        self.symbols: list[str] = []

    def get_quote(self, symbol: str) -> Any:
        self.symbols.append(symbol)
        if self.raises is not None:
            raise self.raises
        return self.quote


class _FakeFmpClient:
    """Stand-in for ``FMPDataClient`` that records construction and close."""

    instances: ClassVar[list[_FakeFmpClient]] = []

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.closed = False
        self.company = _FakeCompany()
        type(self).instances.append(self)

    def close(self) -> None:
        self.closed = True


class TestValidateApiKey:
    def test_valid_key_makes_an_authenticated_quote_probe(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("FMP_API_KEY", raising=False)
        _FakeFmpClient.instances = []
        monkeypatch.setattr("fmp_data.client.FMPDataClient", _FakeFmpClient)

        assert mcp_utils.validate_api_key("KEY123") == (True, "valid")

        assert len(_FakeFmpClient.instances) == 1
        client = _FakeFmpClient.instances[0]
        assert client.kwargs["api_key"] == "KEY123"  # pragma: allowlist secret
        assert client.kwargs["timeout"] == 10
        assert client.kwargs["max_retries"] == 1
        assert client.company.symbols == [mcp_utils._PROBE_SYMBOL]
        assert client.closed is True
        assert "FMP_API_KEY" not in os.environ

    def test_authentication_error_is_invalid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from fmp_data.exceptions import AuthenticationError

        class AuthClient(_FakeFmpClient):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.company = _FakeCompany(
                    raises=AuthenticationError("nope", status_code=401)
                )

        monkeypatch.setattr("fmp_data.client.FMPDataClient", AuthClient)

        assert mcp_utils.validate_api_key("BAD") == (False, "invalid")
        assert AuthClient.instances[-1].closed is True

    def test_config_error_is_invalid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from fmp_data.exceptions import ConfigError

        def boom(**kwargs: Any) -> None:
            raise ConfigError("Invalid client configuration")

        monkeypatch.setattr("fmp_data.client.FMPDataClient", boom)

        assert mcp_utils.validate_api_key("") == (False, "invalid")

    def test_timeout_is_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import httpx

        class TimeoutClient(_FakeFmpClient):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.company = _FakeCompany(raises=httpx.TimeoutException("slow"))

        monkeypatch.setattr("fmp_data.client.FMPDataClient", TimeoutClient)

        assert mcp_utils.validate_api_key("KEY123") == (False, "timeout")

    def test_fmp_timeout_error_is_timeout(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """#350: mapped client timeouts must not count as a valid key."""
        from fmp_data.exceptions import FMPTimeoutError

        class TimeoutClient(_FakeFmpClient):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.company = _FakeCompany(raises=FMPTimeoutError("Request timed out"))

        monkeypatch.setattr("fmp_data.client.FMPDataClient", TimeoutClient)

        assert mcp_utils.validate_api_key("KEY123") == (False, "timeout")
        assert TimeoutClient.instances[-1].closed is True

    def test_fmp_network_error_is_unavailable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """#350: mapped connect failures must not count as a valid key."""
        from fmp_data.exceptions import FMPNetworkError

        class NetworkClient(_FakeFmpClient):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.company = _FakeCompany(raises=FMPNetworkError("Network error"))

        monkeypatch.setattr("fmp_data.client.FMPDataClient", NetworkClient)

        assert mcp_utils.validate_api_key("KEY123") == (False, "unavailable")
        assert NetworkClient.instances[-1].closed is True

    def test_leftover_fmp_network_error_is_unavailable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """#354: non-retryable leftover RequestError mapping is still unavailable."""
        from fmp_data.exceptions import FMPNetworkError

        class TransportClient(_FakeFmpClient):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.company = _FakeCompany(
                    raises=FMPNetworkError("Transport error", retryable=False)
                )

        monkeypatch.setattr("fmp_data.client.FMPDataClient", TransportClient)

        assert mcp_utils.validate_api_key("KEY123") == (False, "unavailable")
        assert TransportClient.instances[-1].closed is True

    def test_httpx_protocol_error_is_unavailable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """#354: raw leftover RequestError fakes stay unavailable."""
        import httpx

        class ProtocolClient(_FakeFmpClient):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                request = httpx.Request("GET", "https://example.test/quote")
                self.company = _FakeCompany(
                    raises=httpx.ProtocolError("broken", request=request)
                )

        monkeypatch.setattr("fmp_data.client.FMPDataClient", ProtocolClient)

        assert mcp_utils.validate_api_key("KEY123") == (False, "unavailable")
        assert ProtocolClient.instances[-1].closed is True

    def test_non_auth_fmp_error_still_counts_as_valid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from fmp_data.exceptions import FMPError

        class BusyClient(_FakeFmpClient):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.company = _FakeCompany(raises=FMPError("rate limited", 429))

        monkeypatch.setattr("fmp_data.client.FMPDataClient", BusyClient)

        assert mcp_utils.validate_api_key("KEY123") == (True, "valid")

    @pytest.mark.parametrize(
        "message",
        [
            "Invalid API KEY",
            "Invalid API KEY. Feel free to create a Free API Key...",
        ],
    )
    def test_typed_2xx_invalid_key_body_is_invalid(
        self, monkeypatch: pytest.MonkeyPatch, message: str
    ) -> None:
        """Wizard invalid follows ``_check_error_response``, not a copy matcher."""
        from fmp_data.base import BaseClient

        class TypingCompany(_FakeCompany):
            def get_quote(self, symbol: str) -> Any:
                self.symbols.append(symbol)
                BaseClient._check_error_response({"Error Message": message})
                return None

        class BodyClient(_FakeFmpClient):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.company = TypingCompany()

        monkeypatch.setattr("fmp_data.client.FMPDataClient", BodyClient)

        assert mcp_utils.validate_api_key("BAD") == (False, "invalid")
        assert BodyClient.instances[-1].closed is True

    def test_statusless_unrelated_fmp_error_is_still_valid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Do not over-match every status-less 200 error body as invalid."""
        from fmp_data.exceptions import FMPError

        class OtherClient(_FakeFmpClient):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.company = _FakeCompany(raises=FMPError("Legacy endpoint retired"))

        monkeypatch.setattr("fmp_data.client.FMPDataClient", OtherClient)

        assert mcp_utils.validate_api_key("KEY123") == (True, "valid")

    def test_http_403_is_invalid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from fmp_data.exceptions import FMPError

        class ForbiddenClient(_FakeFmpClient):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.company = _FakeCompany(
                    raises=FMPError("unauthorized", status_code=403)
                )

        monkeypatch.setattr("fmp_data.client.FMPDataClient", ForbiddenClient)

        assert mcp_utils.validate_api_key("BAD") == (False, "invalid")
        assert ForbiddenClient.instances[-1].closed is True

    def test_unexpected_exception_is_unavailable_not_raised(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class BrokenClient(_FakeFmpClient):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.company = _FakeCompany(raises=OSError("network down"))

        monkeypatch.setattr("fmp_data.client.FMPDataClient", BrokenClient)

        assert mcp_utils.validate_api_key("KEY123") == (False, "unavailable")

    def test_return_never_embeds_exception_text(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        planted = "PLANTED_key_xyzzy"

        class LeakyClient(_FakeFmpClient):
            def __init__(self, **kwargs: Any) -> None:
                super().__init__(**kwargs)
                self.company = _FakeCompany(raises=OSError(f"refused apikey={planted}"))

        monkeypatch.setattr("fmp_data.client.FMPDataClient", LeakyClient)

        ok, reason = mcp_utils.validate_api_key(planted)
        assert ok is False
        assert reason == "unavailable"
        assert planted not in reason


# ---------------------------------------------------------------------------
# get_manifest_choices
# ---------------------------------------------------------------------------


#: Every advertised manifest choice and the file it must come from. Pinning
#: the whole table matters: a test that seeded only two names would keep
#: passing if the other two were dropped from the mapping.
EXAMPLE_MANIFESTS: dict[str, str] = {
    "minimal": "minimal_manifest.py",
    "trading": "trading_manifest.py",
    "research": "research_manifest.py",
    "crypto": "crypto_manifest.py",
}


class TestGetManifestChoices:
    @staticmethod
    def _redirect_examples_root(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> Path:
        monkeypatch.setattr(
            mcp_utils, "__file__", str(tmp_path / "fmp_data" / "mcp" / "utils.py")
        )
        return tmp_path / "examples" / "mcp" / "configurations"

    @pytest.mark.parametrize("name", sorted(EXAMPLE_MANIFESTS))
    def test_each_choice_maps_to_its_own_file_and_only_when_present(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, name: str
    ) -> None:
        examples = self._redirect_examples_root(monkeypatch, tmp_path)
        examples.mkdir(parents=True)
        target = examples / EXAMPLE_MANIFESTS[name]
        target.write_text("TOOLS = []\n", encoding="utf-8")

        assert mcp_utils.get_manifest_choices() == {
            "default": None,
            name: str(target),
        }

    def test_all_choices_are_offered_when_every_example_exists(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        examples = self._redirect_examples_root(monkeypatch, tmp_path)
        examples.mkdir(parents=True)
        for filename in EXAMPLE_MANIFESTS.values():
            (examples / filename).write_text("TOOLS = []\n", encoding="utf-8")

        assert mcp_utils.get_manifest_choices() == {
            "default": None,
            **{
                name: str(examples / filename)
                for name, filename in EXAMPLE_MANIFESTS.items()
            },
        }

    def test_only_default_when_the_examples_tree_is_absent(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        self._redirect_examples_root(monkeypatch, tmp_path)

        assert mcp_utils.get_manifest_choices() == {"default": None}

    def test_repo_example_profiles_are_offered_when_present(self) -> None:
        """The real checkout path, not a redirected fake tree (#320)."""
        repo_examples = (
            Path(__file__).resolve().parents[2] / "examples" / "mcp" / "configurations"
        )
        if not repo_examples.is_dir():
            pytest.skip("example manifests are not shipped in this install")

        choices = mcp_utils.get_manifest_choices()

        assert "default" in choices
        for name, filename in EXAMPLE_MANIFESTS.items():
            expected = repo_examples / filename
            if not expected.is_file():
                pytest.fail(f"advertised example {filename} is missing")
            assert choices[name] == str(expected)


def test_example_claude_desktop_copies_use_the_real_manifest_path() -> None:
    """The same stale path #320 fixed in the helper also lived in examples."""
    root = Path(__file__).resolve().parents[2] / "examples" / "mcp" / "claude_desktop"
    stale = "examples/mcp_configurations/"
    offenders: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".py", ".md", ".json"}:
            continue
        if stale in path.read_text(encoding="utf-8"):
            offenders.append(str(path.relative_to(root)))
    assert not offenders, f"stale examples/mcp_configurations/ in {offenders}"


# ---------------------------------------------------------------------------
# FMP-SEC-001: a Python manifest is parsed as data, never executed
# ---------------------------------------------------------------------------

#: Manifest shapes the restricted parser must refuse. Each one writes
#: ``MARKER`` if it is ever executed, so the absence of that file is the
#: actual security assertion; the raise alone would not distinguish a
#: refusal from a refusal-after-payload.
#:
#: ``subscript`` and ``dunder_attribute`` look redundant but are not: CPython
#: exposes ``__builtins__`` as a dict in some execution contexts and as the
#: module in others, and only one reach-the-``open`` spelling works in each.
REFUSAL_SOURCES: dict[str, str] = {
    "lambda": "TOOLS = [(lambda p: open(p, 'w').write('RAN'))(MARKER)]\n",
    "list_comprehension": "TOOLS = [open(p, 'w').write('RAN') for p in [MARKER]]\n",
    "generator_expression": (
        "TOOLS = list(open(p, 'w').write('RAN') for p in [MARKER])\n"
    ),
    "starred_expression": "TOOLS = [*[open(MARKER, 'w').write('RAN')]]\n",
    "subscript": "TOOLS = [__builtins__['open'](MARKER, 'w').write('RAN')]\n",
    "dunder_attribute": (
        "TOOLS = [__builtins__.__dict__['open'](MARKER, 'w').write('RAN')]\n"
    ),
    "walrus": "TOOLS = [(_p := open(MARKER, 'w').write('RAN'))]\n",
    "ternary": (
        "TOOLS = ['company.profile'] if open(MARKER, 'w').write('RAN') else []\n"
    ),
    "decorated_function": (
        "def _deco(fn):\n"
        "    open(MARKER, 'w').write('RAN')\n"
        "    return fn\n"
        "\n"
        "@_deco\n"
        "def hook():\n"
        "    return None\n"
        "\n"
        "TOOLS = ['company.profile']\n"
    ),
    "class_body": (
        "class Boom:\n"
        "    open(MARKER, 'w').write('RAN')\n"
        "\n"
        "TOOLS = ['company.profile']\n"
    ),
    "augmented_assignment": (
        "TOOLS = ['company.profile']\nTOOLS += [open(MARKER, 'w').write('RAN')]\n"
    ),
    "multiple_targets": "TOOLS = OTHER = [open(MARKER, 'w').write('RAN')]\n",
    "if_statement": (
        "if True:\n    open(MARKER, 'w').write('RAN')\n\nTOOLS = ['company.profile']\n"
    ),
    "for_loop": (
        "for _ in [1]:\n"
        "    open(MARKER, 'w').write('RAN')\n"
        "\n"
        "TOOLS = ['company.profile']\n"
    ),
    "with_statement": (
        "with open(MARKER, 'w') as fh:\n"
        "    fh.write('RAN')\n"
        "\n"
        "TOOLS = ['company.profile']\n"
    ),
    "try_except": (
        "try:\n"
        "    open(MARKER, 'w').write('RAN')\n"
        "except OSError:\n"
        "    pass\n"
        "\n"
        "TOOLS = ['company.profile']\n"
    ),
}


class TestPythonManifestIsParsedAsData:
    @pytest.mark.parametrize("shape", sorted(REFUSAL_SOURCES))
    def test_refuses_the_shape_without_running_its_payload(
        self, tmp_path: Path, shape: str
    ) -> None:
        marker = tmp_path / f"{shape}.ran"
        source = REFUSAL_SOURCES[shape].replace("MARKER", repr(str(marker)))
        manifest = _write_manifest(tmp_path, f"{shape}.py", source)

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert "does not execute" in str(excinfo.value)
        assert str(manifest) in str(excinfo.value)
        assert not marker.exists()

    def test_refuses_a_second_tools_assignment(self, tmp_path: Path) -> None:
        manifest = _write_manifest(
            tmp_path,
            "twice.py",
            "TOOLS = ['company.profile']\nTOOLS = ['market.gainers']\n",
        )

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert "assigned more than once" in str(excinfo.value)

    def test_accepts_an_annotated_tools_assignment(self, tmp_path: Path) -> None:
        """``TOOLS: list[str] = [...]`` is still a data-only assignment."""
        manifest = _write_manifest(
            tmp_path, "annotated.py", "TOOLS: list[str] = ['company.profile']\n"
        )

        assert mcp_utils.load_manifest_tools(manifest) == ["company.profile"]

    @pytest.mark.parametrize(
        ("shape", "source"),
        [
            ("string", "TOOLS = 'company.profile'\n"),
            ("tuple", "TOOLS = ('company.profile',)\n"),
            ("concatenation", "TOOLS = ['company.profile'] + ['market.gainers']\n"),
            ("name_reference", "TOOLS = OTHER_TOOLS\n"),
            ("attribute", "TOOLS = catalog.tools\n"),
            ("dict", "TOOLS = {'company': 'profile'}\n"),
        ],
    )
    def test_tools_must_be_a_list_literal(
        self, tmp_path: Path, shape: str, source: str
    ) -> None:
        manifest = _write_manifest(tmp_path, f"{shape}.py", source)

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert "TOOLS must be a list of string literals" in str(excinfo.value)

    @pytest.mark.parametrize(
        ("shape", "source"),
        [
            ("integer", "TOOLS = [1]\n"),
            ("none", "TOOLS = [None]\n"),
            ("bytes", "TOOLS = [b'company.profile']\n"),
            ("empty_string", "TOOLS = ['']\n"),
            ("nested_list", "TOOLS = [['company.profile']]\n"),
            ("name", "TOOLS = [company_profile]\n"),
        ],
    )
    def test_elements_must_be_non_empty_string_literals(
        self, tmp_path: Path, shape: str, source: str
    ) -> None:
        manifest = _write_manifest(tmp_path, f"element_{shape}.py", source)

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert "TOOLS must contain only non-empty string literals" in str(excinfo.value)

    def test_syntax_error_is_reported_as_an_invalid_manifest(
        self, tmp_path: Path
    ) -> None:
        manifest = _write_manifest(tmp_path, "broken.py", "TOOLS = [\n")

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert str(excinfo.value).startswith(f"Invalid Python manifest {manifest}")
        assert isinstance(excinfo.value.__cause__, SyntaxError)

    def test_docstring_is_allowed_and_empty_tools_is_accepted(
        self, tmp_path: Path
    ) -> None:
        manifest = _write_manifest(
            tmp_path, "empty.py", '"""Nothing enabled."""\n\nTOOLS = []\n'
        )

        assert mcp_utils.load_manifest_tools(manifest) == []

    def test_duplicate_entries_are_returned_verbatim(self, tmp_path: Path) -> None:
        manifest = _write_manifest(
            tmp_path,
            "dupes.py",
            "TOOLS = ['company.profile', 'company.profile', 'market.gainers']\n",
        )

        assert mcp_utils.load_manifest_tools(manifest) == [
            "company.profile",
            "company.profile",
            "market.gainers",
        ]


# ---------------------------------------------------------------------------
# JSON / YAML / TOML manifests
# ---------------------------------------------------------------------------


class TestDataManifestFormats:
    def test_json_suffix_match_is_case_insensitive(self, tmp_path: Path) -> None:
        manifest = _write_manifest(tmp_path, "tools.JSON", '["company.profile"]\n')

        assert mcp_utils.load_manifest_tools(manifest) == ["company.profile"]

    def test_malformed_json_is_wrapped(self, tmp_path: Path) -> None:
        manifest = _write_manifest(tmp_path, "tools.json", "{not json\n")

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert str(excinfo.value).startswith(f"Invalid JSON manifest {manifest}")
        assert isinstance(excinfo.value.__cause__, json.JSONDecodeError)

    def test_json_object_without_tools_key_is_rejected(self, tmp_path: Path) -> None:
        manifest = _write_manifest(tmp_path, "tools.json", '{"enabled": ["a"]}\n')

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert "must be a list of tool specs or an object with a 'tools' list" in str(
            excinfo.value
        )

    def test_tools_key_must_hold_a_list(self, tmp_path: Path) -> None:
        manifest = _write_manifest(
            tmp_path, "tools.json", '{"tools": "company.profile"}\n'
        )

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert "'tools' must be a list of strings" in str(excinfo.value)

    @pytest.mark.parametrize(
        ("shape", "payload"),
        [
            ("integer", '["company.profile", 7]'),
            ("null", '["company.profile", null]'),
            ("empty_string", '["company.profile", ""]'),
            ("nested", '[["company.profile"]]'),
        ],
    )
    def test_json_entries_must_be_non_empty_strings(
        self, tmp_path: Path, shape: str, payload: str
    ) -> None:
        manifest = _write_manifest(tmp_path, f"{shape}.json", payload)

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert "every tool spec must be a non-empty string" in str(excinfo.value)

    def test_duplicate_entries_are_returned_verbatim(self, tmp_path: Path) -> None:
        """Symmetry with the Python path: the parser must not dedupe.

        Listing one tool twice is an error the *loader* reports (#162). A
        parser that quietly collapsed duplicates would swallow it, and no
        other assertion here would notice.
        """
        manifest = _write_manifest(
            tmp_path,
            "dupes.json",
            '["company.profile", "company.profile", "market.gainers"]',
        )

        assert mcp_utils.load_manifest_tools(manifest) == [
            "company.profile",
            "company.profile",
            "market.gainers",
        ]

    def test_yaml_top_level_list(self, tmp_path: Path) -> None:
        """The ``.yaml`` suffix really routes to the YAML parser.

        The comment and unquoted scalars are YAML-only, so a routing bug
        that fell through to JSON (or to the Python parser) would raise
        instead of returning these entries.
        """
        manifest = _write_manifest(
            tmp_path,
            "tools.yaml",
            "# enabled tools\n- company.profile\n- market.gainers\n",
        )

        assert mcp_utils.load_manifest_tools(manifest) == [
            "company.profile",
            "market.gainers",
        ]

    def test_malformed_yaml_is_wrapped(self, tmp_path: Path) -> None:
        yaml = pytest.importorskip("yaml")
        manifest = _write_manifest(tmp_path, "tools.yaml", "tools: [unclosed\n")

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert str(excinfo.value).startswith(f"Invalid YAML manifest {manifest}")
        assert isinstance(excinfo.value.__cause__, yaml.YAMLError)

    def test_empty_yaml_document_is_rejected(self, tmp_path: Path) -> None:
        manifest = _write_manifest(tmp_path, "tools.yaml", "\n")

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert "must be a list of tool specs" in str(excinfo.value)

    def test_yaml_does_not_construct_arbitrary_objects(self, tmp_path: Path) -> None:
        """``safe_load`` refuses python/object tags (no ``yaml.load``)."""
        marker = tmp_path / "pwned"
        manifest = _write_manifest(
            tmp_path,
            "unsafe.yaml",
            f"tools: !!python/object/apply:os.system ['touch {marker}']\n",
        )

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert "Invalid YAML manifest" in str(excinfo.value)
        assert not marker.exists()

    def test_malformed_toml_is_wrapped(self, tmp_path: Path) -> None:
        manifest = _write_manifest(tmp_path, "tools.toml", "tools = [\n")

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert str(excinfo.value).startswith(f"Invalid TOML manifest {manifest}")

    def test_toml_entries_must_be_strings(self, tmp_path: Path) -> None:
        manifest = _write_manifest(tmp_path, "tools.toml", "tools = [1, 2]\n")

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert "every tool spec must be a non-empty string" in str(excinfo.value)


# ---------------------------------------------------------------------------
# path handling
# ---------------------------------------------------------------------------


class TestManifestPathHandling:
    def test_missing_file_raises_with_the_resolved_path(self, tmp_path: Path) -> None:
        missing = tmp_path / "nope.json"

        with pytest.raises(FileNotFoundError) as excinfo:
            mcp_utils.load_manifest_tools(missing)

        assert str(excinfo.value) == f"Manifest file not found: {missing.resolve()}"

    def test_a_directory_is_not_a_manifest(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="Manifest file not found"):
            mcp_utils.load_manifest_tools(tmp_path)

    def test_tilde_is_expanded_before_the_lookup(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        (tmp_path / "tools.json").write_text('["company.profile"]', encoding="utf-8")

        assert mcp_utils.load_manifest_tools("~/tools.json") == ["company.profile"]

    @POSIX_ONLY
    @NOT_ROOT
    def test_unreadable_manifest_raises_permission_error(self, tmp_path: Path) -> None:
        manifest = _write_manifest(tmp_path, "secret.json", '["company.profile"]')
        manifest.chmod(0o000)

        try:
            with pytest.raises(PermissionError):
                mcp_utils.load_manifest_tools(manifest)
        finally:
            manifest.chmod(0o600)

    def test_non_utf8_bytes_raise_a_decode_error(self, tmp_path: Path) -> None:
        manifest = tmp_path / "tools.json"
        manifest.write_bytes(b"\xff\xfe[]")

        with pytest.raises(UnicodeDecodeError):
            mcp_utils.load_manifest_tools(manifest)

    def test_unknown_extension_is_parsed_as_a_python_manifest(
        self, tmp_path: Path
    ) -> None:
        manifest = _write_manifest(
            tmp_path, "tools.txt", "TOOLS = ['company.profile']\n"
        )

        assert mcp_utils.load_manifest_tools(manifest) == ["company.profile"]

    def test_none_returns_a_mutable_copy_of_the_defaults(self) -> None:
        """``DEFAULT_TOOLS`` is a module-level *list*, so this is real.

        The snapshot has to be taken before anything is appended: comparing
        a mutated return value against a freshly read ``DEFAULT_TOOLS``
        compares the aliased list with itself and can never fail. The
        identity check runs first so a regression is caught before it
        corrupts the module global for the rest of the session.
        """
        from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS

        expected = list(DEFAULT_TOOLS)
        assert expected, "floor: an empty default manifest would prove nothing"

        tools = mcp_utils.load_manifest_tools(None)

        assert tools == expected
        assert tools is not DEFAULT_TOOLS

        tools.append("sentinel.not-a-real-tool")

        assert list(DEFAULT_TOOLS) == expected
        assert mcp_utils.load_manifest_tools(None) == expected

    def test_python_manifest_without_tools_names_the_missing_global(
        self, tmp_path: Path
    ) -> None:
        manifest = _write_manifest(
            tmp_path, "docstring_only.py", '"""Just a docstring."""\n'
        )

        with pytest.raises(AttributeError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert str(excinfo.value) == (
            f"{manifest} does not define a global variable 'TOOLS'"
        )

    def test_json_content_under_an_unknown_extension_is_refused(
        self, tmp_path: Path
    ) -> None:
        manifest = _write_manifest(tmp_path, "tools.conf", '["company.profile"]\n')

        with pytest.raises(ValueError) as excinfo:
            mcp_utils.load_manifest_tools(manifest)

        assert "only a docstring and TOOLS" in str(excinfo.value)


# ---------------------------------------------------------------------------
# restart_claude_desktop_instructions
# ---------------------------------------------------------------------------


class TestRestartInstructions:
    @pytest.mark.parametrize(
        ("system", "expected"),
        [
            ("Darwin", "Cmd+Q"),
            ("Windows", "system tray"),
            ("Linux", "application menu"),
        ],
    )
    def test_instructions_are_platform_specific(
        self, monkeypatch: pytest.MonkeyPatch, system: str, expected: str
    ) -> None:
        monkeypatch.setattr(platform, "system", lambda: system)

        text = mcp_utils.restart_claude_desktop_instructions()

        assert expected in text
        assert text.startswith("To restart Claude Desktop")
        steps = text.splitlines()[1:]
        assert [step.strip()[:2] for step in steps] == ["1.", "2.", "3."]

    def test_each_platform_gets_a_distinct_message(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        messages = []
        for system in ("Darwin", "Windows", "Linux"):
            monkeypatch.setattr(platform, "system", lambda s=system: s)
            messages.append(mcp_utils.restart_claude_desktop_instructions())

        assert len(set(messages)) == 3
