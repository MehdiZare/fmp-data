"""Behavioural tests for the Claude Desktop setup wizard.

Relative path: tests/unit/test_mcp_setup.py

Every collaborator that would touch the network, a real Claude install, a
subprocess or the terminal is replaced; the wizard itself never is. The mode
bits of the file ``save_claude_config`` writes are pinned separately in
``tests/unit/test_mcp_config_perms.py`` -- what is asserted here is the
wizard's own behaviour: what it asks, what it redacts, what JSON it merges
and what it returns.
"""

from __future__ import annotations

import getpass
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from types import SimpleNamespace
from typing import Any

import pytest

from fmp_data.mcp import _compat
from fmp_data.mcp import setup as setup_mod
from fmp_data.mcp import utils as mcp_utils
from fmp_data.mcp.setup import SetupWizard, run_setup

CONFIG_NAME = "claude_desktop_config.json"


def feed_input(monkeypatch: pytest.MonkeyPatch, responses: list[str]) -> list[str]:
    """Answer ``input()`` from a queue and record every prompt shown."""
    prompts: list[str] = []
    queue = list(responses)

    def fake_input(prompt: str = "") -> str:
        prompts.append(prompt)
        if not queue:
            raise AssertionError(f"wizard asked one prompt too many: {prompt!r}")
        return queue.pop(0)

    monkeypatch.setattr("builtins.input", fake_input)
    return prompts


def feed_secrets(monkeypatch: pytest.MonkeyPatch, responses: list[str]) -> list[str]:
    """Answer ``getpass.getpass()`` from a queue and record its prompts."""
    prompts: list[str] = []
    queue = list(responses)

    def fake_getpass(prompt: str = "") -> str:
        prompts.append(prompt)
        if not queue:
            raise AssertionError(f"wizard asked for one secret too many: {prompt!r}")
        return queue.pop(0)

    monkeypatch.setattr(getpass, "getpass", fake_getpass)
    return prompts


def record_validations(
    monkeypatch: pytest.MonkeyPatch, verdict: tuple[bool, str]
) -> list[str]:
    """Stand in for ``validate_api_key``, recording every key handed to it."""
    seen: list[str] = []

    def fake_validate(api_key: str) -> tuple[bool, str]:
        seen.append(api_key)
        return verdict

    monkeypatch.setattr(setup_mod, "validate_api_key", fake_validate)
    return seen


def record_server_tests(
    monkeypatch: pytest.MonkeyPatch, verdict: tuple[bool, str]
) -> list[tuple[str, str | None]]:
    """Stand in for ``test_mcp_server``, recording its (key, manifest) pairs."""
    seen: list[tuple[str, str | None]] = []

    def fake_test_server(api_key: str, manifest_path: str | None) -> tuple[bool, str]:
        seen.append((api_key, manifest_path))
        return verdict

    monkeypatch.setattr(setup_mod, "test_mcp_server", fake_test_server)
    return seen


def break_first_error_report(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Make the *first* "Setup failed" write blow up, then behave again.

    That is the only way into ``run_setup``'s fallback reporter without
    stubbing the wizard it is supposed to be exercising.
    """
    real_print = print
    failed_once: list[str] = []

    def flaky_print(*args: Any, **kwargs: Any) -> None:
        text = " ".join(str(arg) for arg in args)
        if "Setup failed" in text and not failed_once:
            failed_once.append(text)
            raise OSError("stdout went away")
        real_print(*args, **kwargs)

    monkeypatch.setattr("builtins.print", flaky_print)
    return failed_once


@pytest.fixture
def claude_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect the Claude Desktop config path in both namespaces."""
    target = tmp_path / "Claude" / CONFIG_NAME
    monkeypatch.setattr(mcp_utils, "get_claude_config_path", lambda: target)
    monkeypatch.setattr(setup_mod, "get_claude_config_path", lambda: target)
    return target


@pytest.fixture
def happy_path(claude_config: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Every collaborator wired so a whole run succeeds offline."""
    monkeypatch.setattr(_compat, "mcp_server_available", lambda: True)
    monkeypatch.setattr(setup_mod, "check_claude_desktop_installed", lambda: True)
    monkeypatch.setattr(setup_mod, "get_api_key_from_env", lambda: "ENV-API-KEY")
    monkeypatch.setattr(setup_mod, "get_manifest_choices", lambda: {"default": None})
    monkeypatch.setattr(setup_mod, "find_python_executable", lambda: "/opt/py")
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0)
    )
    monkeypatch.setattr(
        setup_mod,
        "test_mcp_server",
        lambda key, manifest: (True, "MCP server test passed"),
    )
    return claude_config


class TestRedactSensitive:
    """Nothing secret may reach the terminal, whatever shape it arrives in."""

    def test_none_and_empty_pass_straight_through(self) -> None:
        wizard = SetupWizard()

        assert wizard._redact_sensitive(None) is None
        assert wizard._redact_sensitive("") == ""

    def test_the_configured_key_is_replaced_at_every_occurrence(self) -> None:
        wizard = SetupWizard()
        wizard.api_key = "Kk1Kk2Kk3Kk4"  # pragma: allowlist secret

        redacted = wizard._redact_sensitive("tried Kk1Kk2Kk3Kk4 then Kk1Kk2Kk3Kk4")

        assert redacted == "tried [REDACTED] then [REDACTED]"

    def test_a_query_credential_goes_but_the_rest_of_the_url_stays(self) -> None:
        wizard = SetupWizard()

        redacted = wizard._redact_sensitive(
            "GET https://fmp.test/api/v3/profile?apikey=hunter2xyz&symbol=AAPL"
        )

        assert redacted == (
            "GET https://fmp.test/api/v3/profile?apikey=[REDACTED]&symbol=AAPL"
        )

    @pytest.mark.parametrize(
        "probe",
        [
            "sk-abcdefgh12345678",
            "pk_abcdefgh12345678",
            "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6",  # pragma: allowlist secret
            "deadbeef" * 5,
        ],
    )
    def test_key_shaped_strings_are_redacted_without_being_configured(
        self, probe: str
    ) -> None:
        """The failing-request path prints keys the wizard never held."""
        wizard = SetupWizard()

        redacted = wizard._redact_sensitive(f"request failed for {probe} at 401")

        # Exact equality, not "probe not in redacted": it has to pin that the
        # surrounding words -- including the bare ``401`` -- are left alone.
        assert redacted == "request failed for [REDACTED] at 401"

    @pytest.mark.parametrize(
        "probe",
        [
            "Setup complete for AAPL",
            "Python 3.12.1 detected",
            "config saved to /Users/me/Library/Claude",
        ],
    )
    def test_ordinary_messages_survive_untouched(self, probe: str) -> None:
        """Over-redaction would make the wizard's output useless."""
        assert SetupWizard()._redact_sensitive(probe) == probe


class TestPrint:
    """The styled writer, including the quiet switch."""

    @pytest.mark.parametrize(
        ("style", "expected"),
        [
            ("success", "✅ hello\n"),
            ("error", "❌ hello\n"),
            ("warning", "⚠️  hello\n"),
            ("info", "\U0001f4a1 hello\n"),
            ("", "hello\n"),
        ],
    )
    def test_each_style_gets_its_own_marker(
        self, style: str, expected: str, capsys: pytest.CaptureFixture[str]
    ) -> None:
        SetupWizard().print("hello", style)

        assert capsys.readouterr().out == expected

    def test_the_header_style_is_framed(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        SetupWizard().print("Setup", "header")

        bar = "=" * 60
        assert capsys.readouterr().out == f"\n{bar}\n\U0001f680 Setup\n{bar}\n"

    def test_quiet_mode_writes_nothing_at_all(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        wizard = SetupWizard(quiet=True)

        for style in ("header", "success", "error", "warning", "info", ""):
            wizard.print("hello", style)

        assert capsys.readouterr().out == ""

    def test_printing_redacts_the_configured_key(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        wizard = SetupWizard()
        wizard.api_key = "Kk1Kk2Kk3Kk4"  # pragma: allowlist secret

        wizard.print("saved Kk1Kk2Kk3Kk4", "success")

        out = capsys.readouterr().out
        assert "Kk1Kk2Kk3Kk4" not in out
        assert out == "✅ saved [REDACTED]\n"


class TestPrompts:
    """Input plumbing: defaults, stripping, echo, and re-asking."""

    def test_a_default_is_shown_and_returned_on_an_empty_answer(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        prompts = feed_input(monkeypatch, [""])

        assert SetupWizard().prompt("Continue? (y/n)", "n") == "n"
        assert prompts == ["Continue? (y/n) [n]: "]

    def test_a_typed_answer_wins_and_is_stripped(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        prompts = feed_input(monkeypatch, ["  y  "])

        assert SetupWizard().prompt("Continue? (y/n)", "n") == "y"
        assert prompts == ["Continue? (y/n) [n]: "]

    def test_without_a_default_an_empty_answer_is_the_empty_string(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        prompts = feed_input(monkeypatch, [""])

        assert SetupWizard().prompt("Path") == ""
        assert prompts == ["Path: "]

    def test_a_secret_default_is_hidden_from_the_screen_but_still_returned(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Redaction is a display concern; the caller still needs the value."""
        wizard = SetupWizard()
        wizard.api_key = "Kk1Kk2Kk3Kk4"  # pragma: allowlist secret
        prompts = feed_input(monkeypatch, [""])

        answer = wizard.prompt("Use Kk1Kk2Kk3Kk4?", "Kk1Kk2Kk3Kk4")

        assert answer == "Kk1Kk2Kk3Kk4"
        assert prompts == ["Use [REDACTED]? [[REDACTED]]: "]

    def test_the_key_prompt_goes_through_getpass_and_is_stripped(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        wizard = SetupWizard()
        wizard.api_key = "Kk1Kk2Kk3Kk4"  # pragma: allowlist secret
        prompts = feed_secrets(monkeypatch, ["  typed-key  "])

        assert wizard.prompt_secret("Replace Kk1Kk2Kk3Kk4") == "typed-key"
        assert prompts == ["Replace [REDACTED]: "]

    def test_an_empty_choice_takes_the_default(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        prompts = feed_input(monkeypatch, [""])

        chosen = SetupWizard().prompt_choice("Pick", ["a", "b", "c"], default=1)

        assert chosen == 1
        assert prompts == ["\nSelect (1-3) [2]: "]
        out = capsys.readouterr().out
        assert "    1. a\n" in out
        assert "  > 2. b\n" in out

    def test_a_number_is_translated_to_a_zero_based_index(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        feed_input(monkeypatch, ["3"])

        assert SetupWizard().prompt_choice("Pick", ["a", "b", "c"]) == 2

    def test_an_out_of_range_number_is_rejected_and_re_asked(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        prompts = feed_input(monkeypatch, ["9", "0", "2"])

        chosen = SetupWizard().prompt_choice("Pick", ["a", "b"])

        assert chosen == 1
        assert len(prompts) == 3
        complaint = "Please enter a number between 1 and 2"
        assert capsys.readouterr().out.count(complaint) == 2

    def test_a_non_number_is_rejected_and_re_asked(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        prompts = feed_input(monkeypatch, ["two", "2"])

        chosen = SetupWizard().prompt_choice("Pick", ["a", "b"])

        assert chosen == 1
        assert len(prompts) == 2
        assert "Please enter a valid number" in capsys.readouterr().out


class TestCheckPrerequisites:
    """Each precondition must refuse loudly rather than fail later."""

    @pytest.fixture(autouse=True)
    def _installed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(_compat, "mcp_server_available", lambda: True)
        monkeypatch.setattr(setup_mod, "check_claude_desktop_installed", lambda: True)

    def test_everything_present_passes_without_asking_anything(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        prompts = feed_input(monkeypatch, [])

        assert SetupWizard().check_prerequisites() is True
        assert prompts == []
        out = capsys.readouterr().out
        assert "✅ MCP dependencies are installed" in out
        assert "✅ Claude Desktop detected" in out

    def test_an_old_interpreter_is_refused(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(
            setup_mod,
            "sys",
            SimpleNamespace(
                version_info=SimpleNamespace(major=3, minor=9),
                version="3.9.18 (main)",
                executable=sys.executable,
            ),
        )

        assert SetupWizard().check_prerequisites() is False
        assert "Python 3.10+ required" in capsys.readouterr().out

    def test_an_uninstallable_fmp_data_is_refused(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """``None`` in ``sys.modules`` makes the real import machinery fail."""
        monkeypatch.setitem(sys.modules, "fmp_data", None)

        assert SetupWizard().check_prerequisites() is False
        out = capsys.readouterr().out
        assert "❌ fmp-data package not installed" in out
        assert "pip install fmp-data[mcp]" in out

    def test_a_missing_mcp_extra_is_refused(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(_compat, "mcp_server_available", lambda: False)

        assert SetupWizard().check_prerequisites() is False
        out = capsys.readouterr().out
        assert "❌ MCP dependencies not installed" in out
        assert "pip install fmp-data[mcp]" in out

    def test_a_missing_claude_desktop_is_only_a_warning(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(setup_mod, "check_claude_desktop_installed", lambda: False)
        prompts = feed_input(monkeypatch, ["y"])

        assert SetupWizard().check_prerequisites() is True
        assert prompts == ["Continue anyway? (y/n) [n]: "]
        assert "⚠️  Claude Desktop not detected" in capsys.readouterr().out

    def test_declining_the_warning_stops_the_run(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Enter is enough to stop: the default answer is "n"."""
        monkeypatch.setattr(setup_mod, "check_claude_desktop_installed", lambda: False)
        feed_input(monkeypatch, [""])

        assert SetupWizard().check_prerequisites() is False


class TestSetupApiKey:
    """Key acquisition, validation and the retry loop."""

    def test_the_environment_key_is_adopted_without_validation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(setup_mod, "get_api_key_from_env", lambda: "ENV-API-KEY")
        validated = record_validations(monkeypatch, (True, "ok"))
        prompts = feed_input(monkeypatch, ["y"])
        wizard = SetupWizard()

        assert wizard.setup_api_key() is True
        assert wizard.api_key == "ENV-API-KEY"  # pragma: allowlist secret
        assert validated == []
        assert prompts == ["Use API key from environment? (y/n) [y]: "]

    def test_an_empty_entry_is_refused_and_asked_again(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(setup_mod, "get_api_key_from_env", lambda: None)
        validated = record_validations(monkeypatch, (True, "ok"))
        secrets = feed_secrets(monkeypatch, ["   ", "  GOODKEY  "])
        feed_input(monkeypatch, ["n"])
        wizard = SetupWizard()

        assert wizard.setup_api_key() is True
        assert wizard.api_key == "GOODKEY"  # pragma: allowlist secret
        assert validated == ["GOODKEY"]
        assert len(secrets) == 2
        assert "❌ API key is required" in capsys.readouterr().out

    def test_a_rejected_key_is_reported_redacted_and_then_cleared(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The validator's message quotes the key the user just typed."""
        monkeypatch.setattr(setup_mod, "get_api_key_from_env", lambda: None)
        monkeypatch.setattr(
            setup_mod,
            "validate_api_key",
            lambda key: (False, f"rejected {key} with 401"),
        )
        feed_secrets(monkeypatch, ["Kk1Kk2Kk3Kk4"])
        prompts = feed_input(monkeypatch, ["n"])
        wizard = SetupWizard()

        assert wizard.setup_api_key() is False
        assert wizard.api_key is None
        out = capsys.readouterr().out
        assert "Kk1Kk2Kk3Kk4" not in out
        assert "❌ rejected [REDACTED] with 401" in out
        assert prompts == ["Try another key? (y/n) [y]: "]

    def test_retrying_after_a_rejection_keeps_the_second_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(setup_mod, "get_api_key_from_env", lambda: None)
        monkeypatch.setattr(
            setup_mod,
            "validate_api_key",
            lambda key: (key == "GOOD", "ok" if key == "GOOD" else "bad"),
        )
        feed_secrets(monkeypatch, ["BAD", "GOOD"])
        feed_input(monkeypatch, ["y", "n"])
        wizard = SetupWizard()

        assert wizard.setup_api_key() is True
        assert wizard.api_key == "GOOD"  # pragma: allowlist secret

    def test_saying_yes_to_persistence_prints_shell_instructions(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(setup_mod, "get_api_key_from_env", lambda: None)
        monkeypatch.setattr(setup_mod, "validate_api_key", lambda key: (True, "ok"))
        monkeypatch.setattr(platform, "system", lambda: "Darwin")
        feed_secrets(monkeypatch, ["abcdWXYZabcdWXYZ"])
        feed_input(monkeypatch, ["y"])

        assert SetupWizard().setup_api_key() is True

        out = capsys.readouterr().out
        assert 'export FMP_API_KEY="abcd...WXYZ"' in out  # pragma: allowlist secret
        assert "abcdWXYZabcdWXYZ" not in out

    def test_declining_the_environment_key_falls_through_to_typing_one(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(setup_mod, "get_api_key_from_env", lambda: "ENV-API-KEY")
        monkeypatch.setattr(setup_mod, "validate_api_key", lambda key: (True, "ok"))
        feed_secrets(monkeypatch, ["TYPED-KEY"])
        feed_input(monkeypatch, ["n", "n"])
        wizard = SetupWizard()

        assert wizard.setup_api_key() is True
        assert wizard.api_key == "TYPED-KEY"  # pragma: allowlist secret


class TestShowEnvInstructions:
    """The persistence hint is per-platform and never quotes the whole key."""

    def test_windows_gets_setx(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(platform, "system", lambda: "Windows")

        SetupWizard()._show_env_instructions("abcdWXYZabcdWXYZ")

        out = capsys.readouterr().out
        assert 'setx FMP_API_KEY "abcd...WXYZ"' in out
        assert "abcdWXYZabcdWXYZ" not in out

    @pytest.mark.parametrize(
        ("system", "shell_file"), [("Darwin", "~/.zshrc"), ("Linux", "~/.bashrc")]
    )
    def test_posix_gets_the_right_rc_file(
        self,
        system: str,
        shell_file: str,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr(platform, "system", lambda: system)

        SetupWizard()._show_env_instructions("abcdWXYZabcdWXYZ")

        out = capsys.readouterr().out
        assert f"Add this line to your {shell_file}" in out
        assert f"Then reload with: source {shell_file}" in out

    def test_a_short_key_is_not_partially_revealed(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(platform, "system", lambda: "Linux")

        SetupWizard()._show_env_instructions("12345678")

        out = capsys.readouterr().out
        assert 'export FMP_API_KEY="[YOUR_API_KEY]"' in out
        assert "12345678" not in out


class TestChooseConfiguration:
    """Profile selection, including the degenerate single-profile install."""

    def test_a_lone_default_is_used_without_a_question(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(
            setup_mod, "get_manifest_choices", lambda: {"default": None}
        )
        prompts = feed_input(monkeypatch, [])
        wizard = SetupWizard()

        assert wizard.choose_configuration() is True
        assert wizard.manifest_path is None
        assert prompts == []
        assert "\U0001f4a1 Using default configuration" in capsys.readouterr().out

    def test_a_chosen_profile_becomes_the_manifest_path(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        choices = {
            "default": None,
            "minimal": "/opt/manifests/minimal_manifest.py",
            "crypto": "/opt/manifests/crypto_manifest.py",
        }
        monkeypatch.setattr(setup_mod, "get_manifest_choices", lambda: choices)
        monkeypatch.setattr(
            setup_mod,
            "load_manifest_tools",
            lambda path: ["a", "b", "c"] if path else ["a"] * 40,
        )
        feed_input(monkeypatch, ["2"])
        wizard = SetupWizard()

        assert wizard.choose_configuration() is True
        assert wizard.manifest_path == "/opt/manifests/minimal_manifest.py"
        out = capsys.readouterr().out
        assert "1. Default (40 tools) - Comprehensive toolkit" in out
        assert "2. Minimal (3 tools) - Essential tools only" in out
        assert "3. Crypto (3 tools) - Cryptocurrency focused" in out
        assert "✅ Using minimal configuration" in out

    def test_an_unreadable_manifest_only_costs_the_tool_count(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """A broken example manifest must not abort profile selection."""
        choices = {"default": None, "minimal": "/opt/manifests/minimal_manifest.py"}
        monkeypatch.setattr(setup_mod, "get_manifest_choices", lambda: choices)

        def explode(path: str | None) -> list[str]:
            raise ValueError(f"cannot parse {path}")

        monkeypatch.setattr(setup_mod, "load_manifest_tools", explode)
        feed_input(monkeypatch, ["2"])
        wizard = SetupWizard()

        assert wizard.choose_configuration() is True
        assert wizard.manifest_path == "/opt/manifests/minimal_manifest.py"
        out = capsys.readouterr().out
        assert "2. Minimal - Essential tools only" in out
        assert "tools)" not in out

    def test_picking_the_default_entry_leaves_the_manifest_unset(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        choices = {"default": None, "minimal": "/opt/manifests/minimal_manifest.py"}
        monkeypatch.setattr(setup_mod, "get_manifest_choices", lambda: choices)
        monkeypatch.setattr(setup_mod, "load_manifest_tools", lambda path: ["a"])
        feed_input(monkeypatch, ["1"])
        wizard = SetupWizard()

        assert wizard.choose_configuration() is True
        assert wizard.manifest_path is None
        assert "✅ Using default configuration" in capsys.readouterr().out


class TestFindPython:
    """The interpreter probe -- the only subprocess the wizard spawns itself."""

    @staticmethod
    def _record(
        monkeypatch: pytest.MonkeyPatch, result: Any
    ) -> list[tuple[Any, dict[str, Any]]]:
        calls: list[tuple[Any, dict[str, Any]]] = []

        def fake_run(*args: Any, **kwargs: Any) -> Any:
            calls.append((args[0], kwargs))
            if isinstance(result, Exception):
                raise result
            return result

        monkeypatch.setattr(setup_mod, "find_python_executable", lambda: "/opt/py")
        monkeypatch.setattr(subprocess, "run", fake_run)
        return calls

    def test_an_interpreter_that_imports_fmp_data_is_kept(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        calls = self._record(monkeypatch, SimpleNamespace(returncode=0))
        wizard = SetupWizard()

        assert wizard.find_python() is True
        assert wizard.python_path == "/opt/py"
        assert calls[0][0] == ["/opt/py", "-c", "import fmp_data"]
        assert calls[0][1]["timeout"] == 5
        assert "✅ Found Python: /opt/py" in capsys.readouterr().out

    def test_an_interpreter_without_fmp_data_falls_back_to_the_current_one(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        self._record(monkeypatch, SimpleNamespace(returncode=1))
        wizard = SetupWizard()

        assert wizard.find_python() is True
        assert wizard.python_path == sys.executable
        assert "❌ Python can't import fmp_data" in capsys.readouterr().out

    def test_a_probe_that_blows_up_falls_back_too(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        self._record(monkeypatch, OSError("no such executable"))
        wizard = SetupWizard()

        assert wizard.find_python() is True
        assert wizard.python_path == sys.executable
        assert "\U0001f4a1 Using current Python" in capsys.readouterr().out


class TestUpdateClaudeConfig:
    """The merge into ``claude_desktop_config.json``.

    The real ``load_claude_config`` / ``save_claude_config`` run here; only
    the *path* they resolve is redirected.
    """

    @staticmethod
    def _ready() -> SetupWizard:
        wizard = SetupWizard()
        wizard.python_path = "/opt/py"
        wizard.api_key = "FMP-API-KEY"  # pragma: allowlist secret
        wizard.manifest_path = "/opt/manifests/minimal_manifest.py"
        return wizard

    def test_a_first_run_writes_a_complete_server_entry(
        self,
        claude_config: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        prompts = feed_input(monkeypatch, [])

        assert self._ready().update_claude_config() is True

        written = json.loads(claude_config.read_text(encoding="utf-8"))
        assert written == {
            "mcpServers": {
                "fmp-data": {
                    "command": "/opt/py",
                    "args": ["-m", "fmp_data.mcp"],
                    "env": {
                        "FMP_API_KEY": "FMP-API-KEY",  # pragma: allowlist secret
                        "FMP_MCP_MANIFEST": "/opt/manifests/minimal_manifest.py",
                    },
                }
            }
        }
        assert prompts == []
        out = capsys.readouterr().out
        assert "\U0001f4a1 Creating new Claude configuration" in out
        assert "Configuration saved to:" in out
        assert "Backup created at:" not in out

    @pytest.mark.skipif(os.name == "nt", reason="POSIX mode bits")
    def test_the_wizard_does_not_bypass_the_owner_only_writer(
        self, claude_config: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The file holds an API key, so the wizard's path must be 0600 too."""
        feed_input(monkeypatch, [])

        assert self._ready().update_claude_config() is True
        assert claude_config.stat().st_mode & 0o777 == 0o600

    def test_unrelated_configuration_survives_the_merge(
        self,
        claude_config: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        claude_config.parent.mkdir(parents=True)
        original = json.dumps(
            {
                "globalShortcut": "Alt+Space",
                "mcpServers": {"other": {"command": "node", "args": ["x.js"]}},
            },
            indent=2,
        )
        claude_config.write_text(original, encoding="utf-8")
        feed_input(monkeypatch, [])

        assert self._ready().update_claude_config() is True

        written = json.loads(claude_config.read_text(encoding="utf-8"))
        assert written["globalShortcut"] == "Alt+Space"
        assert written["mcpServers"]["other"] == {"command": "node", "args": ["x.js"]}
        env = written["mcpServers"]["fmp-data"]["env"]
        assert env["FMP_API_KEY"] == "FMP-API-KEY"  # pragma: allowlist secret

        backups = list(claude_config.parent.glob("*.backup_*.json"))
        assert len(backups) == 1
        saved = json.loads(backups[0].read_text(encoding="utf-8"))
        assert saved == json.loads(original)
        assert "\U0001f4a1 Backup created at:" in capsys.readouterr().out

    def test_declining_the_overwrite_leaves_the_file_byte_identical(
        self, claude_config: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        claude_config.parent.mkdir(parents=True)
        original = json.dumps(
            {"mcpServers": {"fmp-data": {"command": "old", "env": {}}}}
        )
        claude_config.write_text(original, encoding="utf-8")
        prompts = feed_input(monkeypatch, ["n"])

        assert self._ready().update_claude_config() is False

        assert claude_config.read_text(encoding="utf-8") == original
        assert list(claude_config.parent.glob("*.backup_*.json")) == []
        assert prompts == ["FMP Data server already configured. Overwrite? (y/n) [y]: "]

    def test_accepting_the_overwrite_replaces_the_stored_key(
        self, claude_config: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        claude_config.parent.mkdir(parents=True)
        claude_config.write_text(
            json.dumps(
                {
                    "mcpServers": {
                        "fmp-data": {
                            "command": "old",
                            "env": {
                                "FMP_API_KEY": "STALE",  # pragma: allowlist secret
                            },
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        feed_input(monkeypatch, ["y"])

        assert self._ready().update_claude_config() is True

        server = json.loads(claude_config.read_text(encoding="utf-8"))["mcpServers"][
            "fmp-data"
        ]
        assert server["command"] == "/opt/py"
        assert server["env"] == {
            "FMP_API_KEY": "FMP-API-KEY",  # pragma: allowlist secret
            "FMP_MCP_MANIFEST": "/opt/manifests/minimal_manifest.py",
        }

    def test_no_manifest_means_no_manifest_variable(
        self, claude_config: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        feed_input(monkeypatch, [])
        wizard = self._ready()
        wizard.manifest_path = None

        assert wizard.update_claude_config() is True

        server = json.loads(claude_config.read_text(encoding="utf-8"))["mcpServers"][
            "fmp-data"
        ]
        expected_key = "FMP-API-KEY"  # pragma: allowlist secret
        assert server["env"] == {"FMP_API_KEY": expected_key}

    def test_a_missing_python_path_refuses_to_write_anything(
        self,
        claude_config: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        feed_input(monkeypatch, [])
        wizard = self._ready()
        wizard.python_path = None

        assert wizard.update_claude_config() is False
        assert not claude_config.exists()
        assert "❌ Python path not set" in capsys.readouterr().out

    def test_a_missing_api_key_refuses_to_write_anything(
        self,
        claude_config: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        feed_input(monkeypatch, [])
        wizard = self._ready()
        wizard.api_key = None

        assert wizard.update_claude_config() is False
        assert not claude_config.exists()
        assert "❌ API key not set" in capsys.readouterr().out

    def test_malformed_existing_json_is_not_swallowed(
        self, claude_config: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Overwriting a hand-edited config on a parse error would lose it."""
        claude_config.parent.mkdir(parents=True)
        claude_config.write_text("{ not json", encoding="utf-8")
        feed_input(monkeypatch, [])

        with pytest.raises(json.JSONDecodeError):
            self._ready().update_claude_config()

        assert claude_config.read_text(encoding="utf-8") == "{ not json"

    def test_a_json_document_that_is_not_an_object_is_rejected(
        self, claude_config: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        claude_config.parent.mkdir(parents=True)
        claude_config.write_text('["mcpServers"]', encoding="utf-8")
        feed_input(monkeypatch, [])

        with pytest.raises(TypeError, match="must be an object"):
            self._ready().update_claude_config()


class TestServerSmokeTest:
    """``SetupWizard.test_server`` -- the pre-flight launch check."""

    def test_without_a_key_the_check_is_skipped_rather_than_failed(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        calls = record_server_tests(monkeypatch, (True, "ok"))

        assert SetupWizard().test_server() is True
        assert calls == []
        assert "⚠️  API key not set, skipping test" in capsys.readouterr().out

    def test_a_passing_check_forwards_key_and_manifest(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        calls = record_server_tests(monkeypatch, (True, "MCP server test passed"))
        wizard = SetupWizard()
        wizard.api_key = "FMP-API-KEY"  # pragma: allowlist secret
        wizard.manifest_path = "/opt/manifests/minimal_manifest.py"

        assert wizard.test_server() is True
        assert calls == [("FMP-API-KEY", "/opt/manifests/minimal_manifest.py")]
        assert "✅ MCP server test passed" in capsys.readouterr().out

    def test_a_failing_check_reports_redacted_and_says_it_is_not_fatal(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(
            setup_mod,
            "test_mcp_server",
            lambda key, manifest: (False, f"boot failed using {key}"),
        )
        wizard = SetupWizard()
        wizard.api_key = "Kk1Kk2Kk3Kk4"  # pragma: allowlist secret

        assert wizard.test_server() is False

        out = capsys.readouterr().out
        assert "Kk1Kk2Kk3Kk4" not in out
        assert "❌ boot failed using [REDACTED]" in out
        assert "may still work with Claude Desktop" in out


class TestShowNextSteps:
    def test_the_closing_screen_carries_the_platform_restart_recipe(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(platform, "system", lambda: "Darwin")

        SetupWizard().show_next_steps()

        out = capsys.readouterr().out
        # Current behaviour, warts and all: the title is passed as
        # "\nSetup Complete!", so the header's rocket ends up alone on its
        # own line inside the banner instead of leading the title.
        assert "\U0001f680 \nSetup Complete!" in out
        assert "1. Restart Claude Desktop completely" in out
        assert "To restart Claude Desktop on macOS:" in out
        assert "Cmd+Q" in out


class TestRun:
    """The whole wizard, end to end, with only the outside world faked."""

    def test_a_successful_run_writes_the_config_and_returns_true(
        self,
        happy_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        prompts = feed_input(monkeypatch, ["y"])
        wizard = SetupWizard()

        assert wizard.run() is True

        written = json.loads(happy_path.read_text(encoding="utf-8"))
        assert written["mcpServers"]["fmp-data"] == {
            "command": "/opt/py",
            "args": ["-m", "fmp_data.mcp"],
            "env": {"FMP_API_KEY": "ENV-API-KEY"},  # pragma: allowlist secret
        }
        assert prompts == ["Use API key from environment? (y/n) [y]: "]
        assert "Setup Complete!" in capsys.readouterr().out

    def test_failed_prerequisites_stop_before_any_question_about_keys(
        self, happy_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(_compat, "mcp_server_available", lambda: False)
        feed_input(monkeypatch, [])

        assert SetupWizard().run() is False
        assert not happy_path.exists()

    def test_giving_up_on_the_api_key_cancels_the_run(
        self,
        happy_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr(setup_mod, "get_api_key_from_env", lambda: None)
        monkeypatch.setattr(setup_mod, "validate_api_key", lambda key: (False, "nope"))
        feed_secrets(monkeypatch, ["BADKEY"])
        feed_input(monkeypatch, ["n"])

        assert SetupWizard().run() is False
        assert not happy_path.exists()
        assert "⚠️  Setup cancelled" in capsys.readouterr().out

    def test_a_failing_smoke_test_can_be_overridden(
        self, happy_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            setup_mod, "test_mcp_server", lambda key, manifest: (False, "no server")
        )
        prompts = feed_input(monkeypatch, ["y", "y"])

        assert SetupWizard().run() is True
        assert happy_path.exists()
        assert prompts[1] == "Continue with setup anyway? (y/n) [y]: "

    def test_a_failing_smoke_test_can_also_end_the_run(
        self, happy_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            setup_mod, "test_mcp_server", lambda key, manifest: (False, "no server")
        )
        feed_input(monkeypatch, ["y", "n"])

        assert SetupWizard().run() is False
        assert not happy_path.exists()

    def test_refusing_to_overwrite_ends_the_run(
        self, happy_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        happy_path.parent.mkdir(parents=True)
        original = json.dumps({"mcpServers": {"fmp-data": {"command": "old"}}})
        happy_path.write_text(original, encoding="utf-8")
        feed_input(monkeypatch, ["y", "n"])

        assert SetupWizard().run() is False

        assert happy_path.read_text(encoding="utf-8") == original
        assert list(happy_path.parent.glob("*.backup_*.json")) == []


class TestRunSetup:
    """The ``run_setup`` entry point: exit codes and crash handling."""

    def test_success_exits_zero(
        self, happy_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        feed_input(monkeypatch, ["y"])

        assert run_setup() == 0

        # The exit code alone would also be returned by a ``run_setup`` that
        # never drove a wizard, so pin the side effect it is reporting on.
        written = json.loads(happy_path.read_text(encoding="utf-8"))
        assert written["mcpServers"]["fmp-data"]["env"] == {
            "FMP_API_KEY": "ENV-API-KEY"  # pragma: allowlist secret
        }

    def test_quiet_mode_reaches_the_wizard(
        self,
        happy_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        feed_input(monkeypatch, ["y"])

        assert run_setup(quiet=True) == 0
        assert capsys.readouterr().out == ""
        assert happy_path.exists()

    def test_a_refused_run_exits_one(
        self, happy_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(_compat, "mcp_server_available", lambda: False)
        feed_input(monkeypatch, [])

        assert run_setup() == 1
        assert not happy_path.exists()

    def test_ctrl_c_is_reported_as_a_cancellation(
        self,
        happy_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        def interrupt() -> bool:
            raise KeyboardInterrupt

        monkeypatch.setattr(setup_mod, "check_claude_desktop_installed", interrupt)

        assert run_setup() == 1
        assert "Setup cancelled by user" in capsys.readouterr().out
        assert not happy_path.exists()

    def test_an_unexpected_crash_is_reported_with_its_key_redacted(
        self,
        happy_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        def explode() -> bool:
            raise RuntimeError("probe hit sk-abcdefgh12345678")

        monkeypatch.setattr(setup_mod, "check_claude_desktop_installed", explode)

        assert run_setup() == 1

        out = capsys.readouterr().out
        assert "❌ Setup failed: probe hit [REDACTED]" in out
        assert "sk-abcdefgh12345678" not in out

    def test_when_the_error_report_itself_fails_the_key_is_still_redacted(
        self,
        happy_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """The fallback wizard must inherit the key it has to hide.

        ``ENV-API-KEY`` matches none of the key-shaped patterns, so only the
        copied ``api_key`` can redact it here.
        """

        def explode() -> dict[str, str | None]:
            raise RuntimeError("manifest scan died holding ENV-API-KEY")

        monkeypatch.setattr(setup_mod, "get_manifest_choices", explode)
        feed_input(monkeypatch, ["y"])
        failed_once = break_first_error_report(monkeypatch)

        assert run_setup() == 1

        out = capsys.readouterr().out
        assert failed_once, "the first error report never happened"
        assert "Setup failed: manifest scan died holding [REDACTED]" in out
        assert "ENV-API-KEY" not in out

    def test_the_fallback_report_survives_a_crash_before_any_key_exists(
        self,
        happy_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """No key to copy is not a reason to lose the error message."""

        def explode() -> bool:
            raise RuntimeError("claude probe died")

        monkeypatch.setattr(setup_mod, "check_claude_desktop_installed", explode)
        failed_once = break_first_error_report(monkeypatch)

        assert run_setup() == 1

        out = capsys.readouterr().out
        assert failed_once, "the first error report never happened"
        assert "❌ Setup failed: claude probe died" in out
