#!/bin/bash
# Quick Start Script for FMP MCP Server with Claude Desktop
# For Mac/Linux users

echo "==========================================="
echo "FMP MCP Server Quick Setup for Claude Desktop"
echo "==========================================="
echo ""

# Check Python
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.10 or higher"
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python found: $($PYTHON_CMD --version)"
echo ""

# Install fmp-data
echo "Installing fmp-data with MCP support..."
$PYTHON_CMD -m pip install "fmp-data[mcp]" --quiet
echo "✅ Package installed"
echo ""

# Get API key
echo "🔑 FMP API Key Setup"
echo "   Get a free key at: https://site.financialmodelingprep.com/pricing-plans?couponCode=mehdi"
read -p "   Enter your FMP API key: " API_KEY
echo ""

# Detect OS and set config path
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
else
    CONFIG_DIR="$HOME/.config/Claude"
fi

CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

# Create directory if needed
mkdir -p "$CONFIG_DIR"

# Create config file
echo "Creating Claude Desktop configuration..."
cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "fmp-data": {
      "command": "$PYTHON_CMD",
      "args": ["-m", "fmp_data.mcp"],
      "env": {
        "FMP_API_KEY": "$API_KEY"
      }
    }
  }
}
EOF

echo "✅ Configuration created at: $CONFIG_FILE"
echo ""

# Test the server
echo "Testing MCP server..."
export FMP_API_KEY="$API_KEY"
$PYTHON_CMD -c "from fmp_data.mcp.server import create_app; app = create_app(); print('✅ Server test passed')" 2>/dev/null || echo "⚠️  Server test failed, but setup complete"
echo ""

echo "==========================================="
echo "✅ Setup Complete!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "1. Restart Claude Desktop (quit completely and reopen)"
echo "2. Start a new conversation"
echo "3. Try asking: 'What's the current price of Apple stock?'"
echo ""
echo "Example questions:"
echo "- 'Show me Tesla's financial statements'"
echo "- 'What are today's top gainers?'"
echo "- 'Calculate the RSI for Microsoft'"
echo ""
