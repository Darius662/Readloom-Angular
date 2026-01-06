@echo off
REM Frontend startup script - Run from frontend folder
REM Usage: run.bat

echo Starting Readloom Frontend (Angular)...

REM Get the directory where this script is located
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0

REM Check if node_modules exists
if not exist "%SCRIPT_DIR%node_modules" (
    echo.
    echo Warning: node_modules not found. Installing dependencies...
    cd /d "%SCRIPT_DIR%"
    call npm install
    if errorlevel 1 (
        echo Error installing dependencies
        exit /b 1
    )
)

echo.
echo Starting Angular development server...
echo Frontend will be available at http://localhost:4200
echo Press Ctrl+C to stop
echo.

REM Start the Angular dev server
cd /d "%SCRIPT_DIR%"
call npm start

exit /b %ERRORLEVEL%
