#!/bin/bash

# SmartPark Frontend Setup Script (macOS/Linux)

echo ""
echo "===================================="
echo "SmartPark Frontend Setup"
echo "===================================="
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm is not installed"
    echo ""
    echo "Please install Node.js from: https://nodejs.org/"
    echo "1. Download LTS version"
    echo "2. Run the installer"
    echo "3. Run this script again"
    echo ""
    exit 1
fi

# Verify we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "ERROR: package.json not found"
    echo "Make sure you're in the frontend directory"
    cd "$(dirname "$0")"
fi

echo "[1/3] Checking npm version..."
npm --version
echo ""

echo "[2/3] Installing dependencies..."
echo "This may take a few minutes..."
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: npm install failed"
    exit 1
fi
echo "Dependencies installed successfully!"
echo ""

echo "[3/3] Starting development server..."
echo "Opening http://localhost:3000..."
npm run dev
