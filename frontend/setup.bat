@echo off
REM SmartPark Frontend Setup Script
REM This script installs Node.js dependencies and starts the frontend

echo.
echo ====================================
echo SmartPark Frontend Setup
echo ====================================
echo.

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: npm is not installed or not in PATH
    echo.
    echo Please install Node.js from: https://nodejs.org/
    echo 1. Download LTS version
    echo 2. Run the installer
    echo 3. Restart your computer
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

REM Verify we're in the frontend directory
if not exist "package.json" (
    echo ERROR: package.json not found
    echo Make sure you're in the frontend directory
    cd /d "d:\Kanishk\PROJECT\SMART PARKING\frontend"
)

echo [1/3] Checking npm version...
npm --version
echo.

echo [2/3] Installing dependencies...
echo This may take a few minutes...
npm install
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: npm install failed
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

echo [3/3] Starting development server...
echo Opening http://localhost:3000 in 3 seconds...
timeout /t 3 /nobreak
npm run dev

pause
