#!/bin/bash

# Test Tauri Desktop Build
# This script tests the Tauri app in development mode

set -e

echo "🧪 Testing Sentinel Tauri Desktop App"
echo "======================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found"
    exit 1
fi
echo "✅ npm: $(npm --version)"

# Check Rust
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust not found. Please install Rust from https://rustup.rs/"
    exit 1
fi
echo "✅ Rust: $(cargo --version)"

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python: $(python3 --version)"
elif command -v python &> /dev/null; then
    echo "✅ Python: $(python --version)"
else
    echo "❌ Python not found. Please install Python 3.11+"
    exit 1
fi

echo ""
echo "📦 Installing dependencies..."
npm install

echo ""
echo "🔍 Checking backend dependencies..."
cd ../sentinel-core
if [ -f "requirements.txt" ]; then
    echo "ℹ️  Backend requirements found. Install with: pip install -r requirements.txt"
else
    echo "⚠️  No requirements.txt found in sentinel-core"
fi
cd ../sentinel-web

echo ""
echo "🚀 Starting Tauri in development mode..."
echo "ℹ️  This will:"
echo "   1. Start Next.js dev server"
echo "   2. Launch Tauri window"
echo "   3. Start Python backend"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run tauri:dev
