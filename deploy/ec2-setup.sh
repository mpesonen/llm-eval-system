#!/bin/bash
# EC2 Setup Script for LLM Eval System
# Tested on: Amazon Linux 2023, Ubuntu 22.04
# Usage: curl -sSL <raw-url> | bash

set -e

echo "=========================================="
echo "  LLM Eval System - EC2 Setup"
echo "=========================================="

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect OS"
    exit 1
fi

echo "Detected OS: $OS"

# Install dependencies based on OS
if [ "$OS" = "amzn" ]; then
    echo "Installing dependencies for Amazon Linux..."
    sudo dnf update -y
    sudo dnf install -y python3.11 python3.11-pip git
    PYTHON_CMD="python3.11"
elif [ "$OS" = "ubuntu" ]; then
    echo "Installing dependencies for Ubuntu..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv git curl
    PYTHON_CMD="python3"
else
    echo "Unsupported OS: $OS"
    exit 1
fi

# Install uv (Python package manager)
echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env 2>/dev/null || export PATH="$HOME/.local/bin:$PATH"

# Create app directory
APP_DIR="/opt/llm-eval"
echo "Setting up application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone or update repository
REPO_URL="${REPO_URL:-https://github.com/YOUR_USERNAME/llm-eval-system.git}"
if [ -d "$APP_DIR/.git" ]; then
    echo "Updating existing repository..."
    cd $APP_DIR
    git pull
else
    echo "Cloning repository..."
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi

# Install Python dependencies
echo "Installing Python dependencies..."
cd $APP_DIR
uv sync

# Create data directory for eval runs
sudo mkdir -p /var/lib/llm-eval
sudo chown $USER:$USER /var/lib/llm-eval

# Create environment file
ENV_FILE="/opt/llm-eval/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Creating environment file..."
    cat > $ENV_FILE << 'EOF'
# LLM Eval Environment Configuration
# Add your API keys here

# Required for OpenAI models
OPENAI_API_KEY=your-openai-api-key-here

# Optional: for Gemini models
# GOOGLE_API_KEY=your-google-api-key-here

# Data directory for eval runs
EVAL_RUNS_DIR=/var/lib/llm-eval
EOF
    echo "NOTE: Edit $ENV_FILE to add your API keys"
fi

# Install systemd service
echo "Installing systemd service..."
sudo cp $APP_DIR/deploy/llm-eval.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable llm-eval

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit /opt/llm-eval/.env and add your OPENAI_API_KEY"
echo "2. Start the service: sudo systemctl start llm-eval"
echo "3. Check status: sudo systemctl status llm-eval"
echo "4. View logs: sudo journalctl -u llm-eval -f"
echo ""
echo "The API will be available at http://<your-ec2-ip>:8000"
echo ""
