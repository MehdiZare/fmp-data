# Troubleshooting Guide for FMP MCP Server with Claude Desktop

## Common Issues and Solutions

### 1. Claude doesn't respond with financial data

**Symptoms:**
- Claude responds normally but doesn't fetch financial data
- No indication that MCP tools are being used

**Solutions:**

#### Check API Key
```bash
# Test your API key
python -c "import os; print('API Key set:', 'FMP_API_KEY' in os.environ)"

# Test API key validity
curl "https://financialmodelingprep.com/api/v3/profile/AAPL?apikey=YOUR_KEY_HERE"
```

#### Verify Configuration File Location
```python
# Run this to find config location
python -c "
import platform
from pathlib import Path
import os

system = platform.system()
if system == 'Darwin':
    path = Path.home() / 'Library' / 'Application Support' / 'Claude' / 'claude_desktop_config.json'
elif system == 'Windows':
    path = Path(os.environ['APPDATA']) / 'Claude' / 'claude_desktop_config.json'
else:
    path = Path.home() / '.config' / 'Claude' / 'claude_desktop_config.json'

print(f'Config should be at: {path}')
print(f'File exists: {path.exists()}')
"
```

#### Restart Claude Desktop
1. Completely quit Claude Desktop (not just close the window)
   - Mac: Cmd+Q or Claude > Quit Claude
   - Windows: File > Exit or Alt+F4
   - Linux: File > Quit
2. Wait 5 seconds
3. Reopen Claude Desktop

---

### 2. "MCP server not found" or "Failed to start MCP server"

**Symptoms:**
- Error message when starting Claude
- MCP tools not available in conversation

**Solutions:**

#### Check Python Installation
```bash
# Check Python version
python --version

# Should be 3.10 or higher
# If not found, try:
python3 --version
```

#### Check FMP-Data Installation
```bash
# Check if installed
pip show fmp-data

# If not installed:
pip install "fmp-data[mcp]"

# Or with pip3:
pip3 install "fmp-data[mcp]"
```

#### Fix Python Path in Config
Find your Python executable:
```bash
# Mac/Linux
which python
# or
which python3

# Windows
where python
```

Update your config with the correct path:
```json
{
  "mcpServers": {
    "fmp-data": {
      "command": "/usr/bin/python3",  // Use your actual path
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "your_key"
      }
    }
  }
}
```

---

### 3. Rate Limit Errors

**Symptoms:**
- "Rate limit exceeded" messages
- Claude stops fetching financial data after a few queries

**Solutions:**

#### Check Your API Tier
```python
# Check your current limits
import requests
response = requests.get(
    "https://financialmodelingprep.com/api/v3/profile/AAPL",
    params={"apikey": "YOUR_KEY"}
)
print(f"Remaining calls: {response.headers.get('X-Rate-Limit-Remaining', 'Unknown')}")
print(f"Limit: {response.headers.get('X-Rate-Limit-Limit', 'Unknown')}")
```

#### Reduce Tool Count
Use a minimal configuration to reduce API calls:
```json
{
  "mcpServers": {
    "fmp-data": {
      "command": "python",
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "your_key",
        "FMP_MCP_MANIFEST": "examples/mcp_configurations/minimal_manifest.py"
      }
    }
  }
}
```

---

### 4. JSON Configuration Errors

**Symptoms:**
- Claude won't start
- "Invalid configuration" error

**Solutions:**

#### Validate JSON Syntax
```python
# Test your config file
import json
from pathlib import Path

config_path = Path("path/to/your/claude_desktop_config.json")
try:
    with open(config_path) as f:
        json.load(f)
    print("✅ JSON is valid")
except json.JSONDecodeError as e:
    print(f"❌ JSON error: {e}")
```

#### Common JSON Mistakes
```json
// ❌ WRONG - Comments not allowed
{
  "mcpServers": {
    "fmp-data": {
      ...
    }
  }
}

// ❌ WRONG - Trailing comma
{
  "mcpServers": {
    "fmp-data": {
      "command": "python",
    }  // <- Remove this comma
  }
}

// ❌ WRONG - Single quotes
{
  'mcpServers': {  // <- Must use double quotes
    ...
  }
}

// ✅ CORRECT
{
  "mcpServers": {
    "fmp-data": {
      "command": "python",
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "your_key"
      }
    }
  }
}
```

---

### 5. Testing MCP Server Independently

**Test Script:**
```python
# test_mcp.py
import os
os.environ["FMP_API_KEY"] = "your_key_here"

from fmp_data.mcp.server import create_app

try:
    app = create_app()
    print("✅ MCP server created successfully")

    # Test a simple tool
    from fmp_data import FMPDataClient
    client = FMPDataClient.from_env()
    quote = client.company.get_quote("AAPL")
    print(f"✅ API working - AAPL price: ${quote.price}")

except Exception as e:
    print(f"❌ Error: {e}")
```

Run with:
```bash
python test_mcp.py
```

---

### 6. Windows-Specific Issues

#### PowerShell Execution Policy
```powershell
# Check current policy
Get-ExecutionPolicy

# If Restricted, temporarily allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Path Separators
Use forward slashes or escaped backslashes:
```json
// ✅ Good
"FMP_MCP_MANIFEST": "C:/Users/Name/manifests/my_tools.py"

// ✅ Also good
"FMP_MCP_MANIFEST": "C:\\Users\\Name\\manifests\\my_tools.py"

// ❌ Bad
"FMP_MCP_MANIFEST": "C:\Users\Name\manifests\my_tools.py"
```

---

### 7. Mac-Specific Issues

#### Permission Issues
```bash
# Grant Terminal/Python permissions
# System Preferences > Security & Privacy > Privacy > Full Disk Access
# Add Terminal.app or your Python interpreter
```

#### Library Access
```bash
# Check if config directory exists
ls -la ~/Library/Application\ Support/Claude/

# Create if missing
mkdir -p ~/Library/Application\ Support/Claude/
```

---

### 8. Debug Mode

Create a debug configuration to see detailed logs:

```json
{
  "mcpServers": {
    "fmp-data": {
      "command": "python",
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "your_key",
        "FMP_LOG_LEVEL": "DEBUG",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

---

### 9. Getting Help

#### Check Versions
```bash
# Create a diagnostic report
python -c "
import sys
import platform
import pkg_resources

print('System Information:')
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'Python Path: {sys.executable}')

try:
    fmp_version = pkg_resources.get_distribution('fmp-data').version
    print(f'fmp-data: {fmp_version}')
except:
    print('fmp-data: Not installed')

try:
    import mcp
    print('MCP: Installed')
except:
    print('MCP: Not installed')
"
```

#### Log Files
Check Claude Desktop logs:
- Mac: `~/Library/Logs/Claude/`
- Windows: `%APPDATA%\Claude\logs\`
- Linux: `~/.config/Claude/logs/`

#### Contact Support
- **FMP Data Issues**: [GitHub Issues](https://github.com/MehdiZare/fmp-data/issues)
- **Claude Desktop**: [Claude Support](https://support.anthropic.com)

---

## Quick Fixes Checklist

- [ ] API key is valid and set correctly
- [ ] Python 3.10+ is installed
- [ ] fmp-data[mcp] package is installed
- [ ] Config file is in the right location
- [ ] Config JSON is valid (no syntax errors)
- [ ] Claude Desktop has been fully restarted
- [ ] Python path in config is correct
- [ ] No firewall blocking Python
- [ ] Not exceeding API rate limits

---

## Test Commands

```bash
# 1. Test Python
python --version

# 2. Test package
pip show fmp-data

# 3. Test import
python -c "from fmp_data.mcp.server import create_app; print('Import successful')"

# 4. Test API key
python -c "
import os
import requests
key = os.environ.get('FMP_API_KEY', 'not_set')
if key != 'not_set':
    r = requests.get(f'https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={key}')
    print('API Status:', r.status_code)
else:
    print('API key not set')
"

# 5. Test MCP server
export FMP_API_KEY="your_key"  # or SET on Windows
python -m fmp_data.mcp
```

If all tests pass but Claude still doesn't work, the issue is likely with the Claude Desktop configuration or a need to restart Claude.
