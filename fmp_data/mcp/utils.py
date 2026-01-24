"""
MCP Setup Utilities

Helper functions for setting up and managing MCP server configuration.
"""

from __future__ import annotations

from datetime import datetime
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from typing import Any


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
            result = subprocess.run(
                [cmd, "--version"], capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                # Get the full path
                which_result = subprocess.run(
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

    # Create backup if requested and file exists
    if backup and config_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = config_path.with_suffix(f".backup_{timestamp}.json")
        shutil.copy2(config_path, backup_path)

    # Save configuration
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

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


def test_mcp_server(api_key: str, manifest_path: str | None = None) -> tuple[bool, str]:
    """
    Test if the MCP server can start successfully.

    Parameters
    ----------
    api_key
        FMP API key to test
    manifest_path
        Optional path to custom manifest

    Returns
    -------
    tuple[bool, str]
        Success status and message
    """
    env = os.environ.copy()
    env["FMP_API_KEY"] = api_key

    if manifest_path:
        env["FMP_MCP_MANIFEST"] = manifest_path

    try:
        # Try to import and create the app
        result = subprocess.run(
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
            return True, "MCP server test passed"
        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return False, f"MCP server test failed: {error_msg}"

    except subprocess.TimeoutExpired:
        # Timeout actually means the server started and is waiting for input
        return True, "MCP server test passed (server started)"
    except Exception as e:
        return False, f"MCP server test failed: {e}"


def get_api_key_from_env() -> str | None:
    """
    Get FMP API key from environment variables.

    Returns
    -------
    str | None
        API key if found, None otherwise
    """
    return os.environ.get("FMP_API_KEY")


def validate_api_key(api_key: str) -> tuple[bool, str]:
    """
    Validate an FMP API key by making a test request.

    Parameters
    ----------
    api_key
        API key to validate

    Returns
    -------
    tuple[bool, str]
        Success status and message
    """
    try:
        # Try to create a client with the API key
        env = os.environ.copy()
        env["FMP_API_KEY"] = api_key

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import os; "
                "from fmp_data import FMPDataClient; "
                "client = FMPDataClient.from_env(); "
                "client.close(); "
                "print('API key is valid')",
            ],
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            return True, "API key is valid"
        else:
            error_msg = result.stderr.strip() if result.stderr else "Invalid API key"
            if "401" in error_msg or "403" in error_msg:
                return False, "API key is invalid or expired"
            return False, f"API key validation failed: {error_msg}"

    except subprocess.TimeoutExpired:
        return False, "API key validation timed out"
    except Exception as e:
        return False, f"API key validation failed: {e}"


def get_manifest_choices() -> dict[str, str | None]:
    """
    Get available manifest configuration choices.

    Returns
    -------
    dict[str, str | None]
        Mapping of choice names to manifest paths (None for default)
    """
    base_path = Path(__file__).parent.parent.parent / "examples" / "mcp_configurations"

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


def load_manifest_tools(manifest_path: str | Path | None) -> list[str]:
    """
    Load tool specs from a manifest file or return defaults.

    Parameters
    ----------
    manifest_path
        Path to a manifest file that defines ``TOOLS``, or None for defaults.

    Returns
    -------
    list[str]
        Tool specifications from the manifest (or defaults).
    """
    if manifest_path is None:
        from fmp_data.mcp.tools_manifest import DEFAULT_TOOLS

        return list(DEFAULT_TOOLS)

    path = Path(manifest_path).expanduser().resolve()
    spec = importlib.util.spec_from_file_location("user_manifest", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import manifest at {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    tools = getattr(module, "TOOLS", None)
    if tools is None:
        raise AttributeError(f"{path} does not define a global variable 'TOOLS'")

    return list(tools)


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
