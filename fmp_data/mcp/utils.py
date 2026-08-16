"""
MCP Setup Utilities

Helper functions for setting up and managing MCP server configuration.
"""

from __future__ import annotations

import ast
from datetime import datetime
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess  # nosec B404
import sys
import tempfile
from typing import Any, Literal


def get_claude_config_path() -> Path:
    """
    Get the Claude Desktop configuration file path for the current OS.

    Returns
    -------
    Path
        Path to Claude Desktop configuration file
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "Claude"
            / "claude_desktop_config.json"
        )
    elif system == "Windows":
        return (
            Path(os.environ.get("APPDATA", ""))
            / "Claude"
            / "claude_desktop_config.json"
        )
    else:  # Linux
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def find_python_executable() -> str:
    """
    Find the best Python executable to use for the MCP server.

    Returns
    -------
    str
        Path to Python executable
    """
    # First, try to use the current Python executable
    current_python = sys.executable
    if current_python and Path(current_python).exists():
        return current_python

    # Try common Python commands
    for cmd in ["python3", "python", "python3.10", "python3.11", "python3.12"]:
        try:
            # Fixed argv from the literal list above; no shell.
            result = subprocess.run(  # noqa: S603  # nosec B603
                [cmd, "--version"], capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                # Get the full path
                which_result = subprocess.run(  # noqa: S603  # nosec B603
                    (
                        ["which", cmd]
                        if platform.system() != "Windows"
                        else ["where", cmd]
                    ),
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if which_result.returncode == 0:
                    return which_result.stdout.strip().split("\n")[0]
        except (subprocess.SubprocessError, FileNotFoundError):
            continue

    # Default to system Python
    return "python3"


def check_claude_desktop_installed() -> bool:
    """
    Check if Claude Desktop is installed.

    Returns
    -------
    bool
        True if Claude Desktop appears to be installed
    """
    config_path = get_claude_config_path()

    # Check if config directory exists
    if config_path.parent.exists():
        return True

    # Additional platform-specific checks
    system = platform.system()
    if system == "Darwin":  # macOS
        app_path = Path("/Applications/Claude.app")
        if app_path.exists():
            return True
    elif system == "Windows":
        # Check common installation paths
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        app_path = Path(program_files) / "Claude"
        if app_path.exists():
            return True

    return False


def load_claude_config() -> dict[str, Any]:
    """
    Load the Claude Desktop configuration.

    Returns
    -------
    dict
        Configuration dictionary
    """
    config_path = get_claude_config_path()

    if config_path.exists():
        with open(config_path) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise TypeError("Claude config JSON must be an object")
        return data

    return {}


def _chmod_user_only(path: Path, mode: int) -> None:
    """Best-effort owner-only mode. Windows chmod is a no-op for this bit."""
    if os.name == "nt":
        return
    try:
        os.chmod(path, mode)
    except OSError:
        return


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON via a temp file, then ``os.replace``, mode ``0600``."""
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        _chmod_user_only(tmp_path, 0o600)
        os.replace(tmp_path, path)
        _chmod_user_only(path, 0o600)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def save_claude_config(config: dict[str, Any], backup: bool = True) -> Path | None:
    """
    Save the Claude Desktop configuration.

    Parameters
    ----------
    config
        Configuration dictionary to save
    backup
        Whether to create a backup of existing config

    Returns
    -------
    Path | None
        Path to backup file if created, None otherwise
    """
    config_path = get_claude_config_path()
    backup_path = None

    # Create directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    _chmod_user_only(config_path.parent, 0o700)

    # Create backup if requested and file exists
    if backup and config_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = config_path.with_suffix(f".backup_{timestamp}.json")
        shutil.copy2(config_path, backup_path)
        _chmod_user_only(backup_path, 0o600)

    _atomic_write_json(config_path, config)
    return backup_path


def add_mcp_server_to_config(
    config: dict[str, Any],
    server_name: str,
    python_path: str,
    api_key: str,
    manifest_path: str | None = None,
) -> dict[str, Any]:
    """
    Add or update MCP server configuration.

    Parameters
    ----------
    config
        Existing configuration dictionary
    server_name
        Name for the MCP server
    python_path
        Path to Python executable
    api_key
        FMP API key
    manifest_path
        Optional path to custom manifest

    Returns
    -------
    dict
        Updated configuration
    """
    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Configure the server
    server_config: dict[str, Any] = {
        "command": python_path,
        "args": ["-m", "fmp_data.mcp"],
        "env": {"FMP_API_KEY": api_key},
    }

    # Add custom manifest if specified
    if manifest_path:
        server_config["env"]["FMP_MCP_MANIFEST"] = manifest_path

    config["mcpServers"][server_name] = server_config

    return config


# Classified reasons only. Never embed stderr / exception text — those
# strings can quote the API key, and stdout is a CodeQL logging sink
# (py/clear-text-logging-sensitive-data). Callers must map the reason
# onto a string literal at the print site (#319, #321).
McpServerCheckReason = Literal["passed", "started", "failed", "unavailable"]
ApiKeyCheckReason = Literal["valid", "invalid", "timeout", "unavailable"]

# Cheap authenticated probe used by ``validate_api_key``. Any live symbol
# works; AAPL is on every FMP plan that can call ``quote``.
_PROBE_SYMBOL = "AAPL"


def test_mcp_server(
    api_key: str, manifest_path: str | None = None
) -> tuple[bool, McpServerCheckReason]:
    """Test whether the MCP server process can start.

    Returns a classified reason, never subprocess stderr or exception
    text. ``fmp-mcp status`` / ``test`` must print a sink-local literal
    derived from the reason, not this return value interpolated (#319).
    """
    env = os.environ.copy()
    env["FMP_API_KEY"] = api_key

    if manifest_path:
        env["FMP_MCP_MANIFEST"] = manifest_path

    try:
        # Try to import and create the app
        result = subprocess.run(  # nosec B603
            [
                sys.executable,
                "-c",
                "from fmp_data.mcp.server import create_app; "
                "app = create_app(); "
                "print('Server initialized successfully')",
            ],
            env=env,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            return True, "passed"
        return False, "failed"

    except subprocess.TimeoutExpired:
        # Timeout actually means the server started and is waiting for input
        return True, "started"
    except Exception:
        return False, "unavailable"


def get_api_key_from_env() -> str | None:
    """
    Get FMP API key from environment variables.

    Returns
    -------
    str | None
        API key if found, None otherwise
    """
    return os.environ.get("FMP_API_KEY")


def validate_api_key(api_key: str) -> tuple[bool, ApiKeyCheckReason]:
    """Validate an FMP API key with a cheap authenticated request.

    Constructs a client and calls ``company.get_quote`` so a typed junk
    key cannot report success (#317). Returns a classified reason, never
    exception text or stderr — those can quote the key (#319).
    """
    import httpx

    from fmp_data.client import FMPDataClient
    from fmp_data.exceptions import AuthenticationError, ConfigError, FMPError

    client: FMPDataClient | None = None
    try:
        # One attempt: 401 is not retried, and a 4-10s backoff would make
        # the wizard feel hung on a network blip.
        client = FMPDataClient(api_key=api_key, timeout=10, max_retries=1)
        client.company.get_quote(_PROBE_SYMBOL)
    except AuthenticationError:
        return False, "invalid"
    except ConfigError:
        return False, "invalid"
    except (TimeoutError, httpx.TimeoutException):
        return False, "timeout"
    except FMPError as exc:
        # HTTP 401 and 2xx invalid-key bodies are AuthenticationError
        # (#340). 403 is still a generic FMPError. 429 / 5xx mean the
        # key was accepted.
        if exc.status_code in {401, 403}:
            return False, "invalid"
        return True, "valid"
    except Exception:
        return False, "unavailable"
    finally:
        if client is not None:
            client.close()
    return True, "valid"


def get_manifest_choices() -> dict[str, str | None]:
    """
    Get available manifest configuration choices.

    Returns
    -------
    dict[str, str | None]
        Mapping of choice names to manifest paths (None for default)
    """
    base_path = (
        Path(__file__).resolve().parent.parent.parent
        / "examples"
        / "mcp"
        / "configurations"
    )

    choices: dict[str, str | None] = {
        "default": None,  # Use default manifest
    }

    # Add example manifests if they exist
    manifest_files = {
        "minimal": "minimal_manifest.py",
        "trading": "trading_manifest.py",
        "research": "research_manifest.py",
        "crypto": "crypto_manifest.py",
    }

    for name, filename in manifest_files.items():
        manifest_path = base_path / filename
        if manifest_path.exists():
            choices[name] = str(manifest_path)

    return choices


def _coerce_tool_list(data: Any, path: Path) -> list[str]:
    """Accept a top-level list or an object with a ``tools`` list of strings."""
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict) and "tools" in data:
        items = data["tools"]
    else:
        raise ValueError(
            f"{path} must be a list of tool specs or an object with a "
            "'tools' list of strings"
        )
    if not isinstance(items, list):
        raise ValueError(f"{path}: 'tools' must be a list of strings")
    tools: list[str] = []
    for item in items:
        if not isinstance(item, str) or not item:
            raise ValueError(f"{path}: every tool spec must be a non-empty string")
        tools.append(item)
    return tools


def _string_list_from_ast(node: ast.AST, path: Path) -> list[str]:
    if not isinstance(node, ast.List):
        raise ValueError(
            f"{path} is not a data-only manifest: TOOLS must be a list of "
            "string literals. A Python manifest does not execute."
        )
    tools: list[str] = []
    for elt in node.elts:
        if (
            not isinstance(elt, ast.Constant)
            or not isinstance(elt.value, str)
            or not elt.value
        ):
            raise ValueError(
                f"{path} is not a data-only manifest: TOOLS must contain only "
                "non-empty string literals. A Python manifest does not execute."
            )
        tools.append(elt.value)
    return tools


def _tools_list_from_assignment(
    stmt: ast.Assign | ast.AnnAssign, path: Path, already: list[str] | None
) -> list[str]:
    """Extract ``TOOLS`` from a module-level assignment or annotated assignment."""
    value: ast.expr | None
    if isinstance(stmt, ast.Assign):
        ok = (
            len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name)
            and stmt.targets[0].id == "TOOLS"
        )
        value = stmt.value
    else:
        ok = isinstance(stmt.target, ast.Name) and stmt.target.id == "TOOLS"
        value = stmt.value
    if not ok or value is None:
        raise ValueError(
            f"{path} is not a data-only manifest: only a module-level "
            "TOOLS = [...] assignment is allowed. A Python manifest "
            "does not execute."
        )
    if already is not None:
        raise ValueError(
            f"{path} is not a data-only manifest: TOOLS is assigned "
            "more than once. A Python manifest does not execute."
        )
    return _string_list_from_ast(value, path)


def _parse_python_manifest(source: str, path: Path) -> list[str]:
    """Parse a legacy ``TOOLS = ["..."]`` file without executing it."""
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        raise ValueError(f"Invalid Python manifest {path}: {exc}") from exc

    tools: list[str] | None = None
    for stmt in tree.body:
        if (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Constant)
            and isinstance(stmt.value.value, str)
        ):
            continue
        if isinstance(stmt, ast.Assign | ast.AnnAssign):
            tools = _tools_list_from_assignment(stmt, path, tools)
            continue
        raise ValueError(
            f"{path} is not a data-only manifest: only a docstring and "
            "TOOLS = [...] are allowed. A Python manifest does not execute."
        )

    if tools is None:
        raise AttributeError(f"{path} does not define a global variable 'TOOLS'")
    return tools


def _load_json_manifest(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON manifest {path}: {exc}") from exc
    return _coerce_tool_list(data, path)


def _load_yaml_manifest(path: Path) -> list[str]:
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError(
            f"Cannot load {path}: PyYAML is required for YAML manifests. "
            "Install with: pip install 'fmp-data[mcp]'"
        ) from exc
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML manifest {path}: {exc}") from exc
    return _coerce_tool_list(data, path)


def _load_toml_manifest(path: Path) -> list[str]:
    try:
        import tomllib
    except ImportError:  # pragma: no cover - Python 3.10
        try:
            import tomli as tomllib  # type: ignore[no-redef]
        except ImportError as exc:
            raise RuntimeError(
                f"Cannot load {path}: TOML manifests need tomli on Python "
                "3.10. Install with: pip install 'fmp-data[mcp]'"
            ) from exc
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Invalid TOML manifest {path}: {exc}") from exc
    return _coerce_tool_list(data, path)


def load_manifest_tools(manifest_path: str | Path | None) -> list[str]:
    """
    Load tool specs from a data-only manifest, or return defaults.

    Python files are parsed as a restricted ``TOOLS = ["..."]`` assignment.
    They are never imported or executed. JSON and YAML accept a top-level
    list or an object with a ``tools`` list. TOML accepts only a ``tools``
    array (no top-level TOML array). On Python 3.10 TOML parsing uses
    ``tomli`` from the mcp extra.

    Parameters
    ----------
    manifest_path
        Path to a manifest file, or None for defaults.

    Returns
    -------
    list[str]
        Tool specifications from the manifest (or defaults).
    """
    if manifest_path is None:
        from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS

        return list(DEFAULT_TOOLS)

    path = Path(manifest_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Manifest file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        return _load_json_manifest(path)
    if suffix in {".yaml", ".yml"}:
        return _load_yaml_manifest(path)
    if suffix == ".toml":
        return _load_toml_manifest(path)

    return _parse_python_manifest(path.read_text(encoding="utf-8"), path)


def restart_claude_desktop_instructions() -> str:
    """
    Get platform-specific instructions for restarting Claude Desktop.

    Returns
    -------
    str
        Instructions for restarting Claude Desktop
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        return (
            "To restart Claude Desktop on macOS:\n"
            "  1. Click the Claude icon in the menu bar\n"
            "  2. Select 'Quit Claude' or press Cmd+Q\n"
            "  3. Open Claude Desktop again from Applications or Spotlight"
        )
    elif system == "Windows":
        return (
            "To restart Claude Desktop on Windows:\n"
            "  1. Right-click the Claude icon in the system tray\n"
            "  2. Select 'Exit' or 'Quit'\n"
            "  3. Open Claude Desktop again from the Start Menu"
        )
    else:  # Linux
        return (
            "To restart Claude Desktop:\n"
            "  1. Close all Claude Desktop windows\n"
            "  2. Ensure the process is terminated\n"
            "  3. Open Claude Desktop again from your application menu"
        )
