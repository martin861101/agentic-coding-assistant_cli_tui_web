#!/bin/bash

# ARIA Setup Script
# This script sets up ARIA on your Ubuntu server

echo "🚀 Setting up ARIA - Adaptive Real-time Intelligence Assistant"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install Chromium for web automation
echo ""
echo "🌐 Installing Chromium for web automation..."
if command -v chromium-browser &> /dev/null; then
    echo "✓ Chromium already installed"
else
    echo "Installing Chromium and ChromeDriver..."
    sudo apt update
    sudo apt install -y chromium-browser chromium-chromedriver
    echo "✓ Chromium installed"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✓ Created .env file. Please edit it with your settings."
else
    echo "✓ .env file already exists"
fi

# Check if Ollama is installed
echo ""
echo "🔍 Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed."
    echo ""
    echo "To install Ollama, run:"
    echo "  curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    echo "Then pull a model:"
    echo "  ollama pull llama3"
else
    echo "✓ Ollama found: $(ollama --version)"
    
    # Check if llama3 model is available
    if ollama list | grep -q "llama3"; then
        echo "✓ llama3 model is available"
    else
        echo "⚠️  llama3 model not found. Pulling it now..."
        ollama pull llama3
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start ARIA:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run ARIA: python aria.py"
echo ""
echo "Enjoy using ARIA! 🚀"
