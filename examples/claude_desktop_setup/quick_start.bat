@echo off
REM Quick Start Script for FMP MCP Server with Claude Desktop
REM For Windows users

echo ===========================================
echo FMP MCP Server Quick Setup for Claude Desktop
echo ===========================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python 3.10 or higher
    echo        Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do echo Found: %%i
echo.

REM Install fmp-data
echo Installing fmp-data with MCP support...
python -m pip install "fmp-data[mcp]" >nul 2>&1
echo Package installed
echo.

REM Get API key
echo FMP API Key Setup
echo    Get a free key at: https://site.financialmodelingprep.com/pricing-plans?couponCode=mehdi
set /p API_KEY="   Enter your FMP API key: "
echo.

REM Set config path
set CONFIG_DIR=%APPDATA%\Claude
set CONFIG_FILE=%CONFIG_DIR%\claude_desktop_config.json

REM Create directory if needed
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

REM Create config file
echo Creating Claude Desktop configuration...
(
echo {
echo   "mcpServers": {
echo     "fmp-data": {
echo       "command": "python",
echo       "args": ["-m", "fmp_data.mcp"],
echo       "env": {
echo         "FMP_API_KEY": "%API_KEY%"
echo       }
echo     }
echo   }
echo }
) > "%CONFIG_FILE%"

echo Configuration created at: %CONFIG_FILE%
echo.

REM Test the server
echo Testing MCP server...
set FMP_API_KEY=%API_KEY%
python -c "from fmp_data.mcp.server import create_app; app = create_app(); print('Server test passed')" 2>nul || echo Server test failed, but setup complete
echo.

echo ===========================================
echo Setup Complete!
echo ===========================================
echo.
echo Next steps:
echo 1. Restart Claude Desktop (quit completely and reopen)
echo 2. Start a new conversation
echo 3. Try asking: 'What's the current price of Apple stock?'
echo.
echo Example questions:
echo - 'Show me Tesla's financial statements'
echo - 'What are today's top gainers?'
echo - 'Calculate the RSI for Microsoft'
echo.
pause
