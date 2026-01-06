@echo off
REM Backend startup script - Run from backend folder
REM Usage: run.bat

echo Starting Readloom Backend...

REM Get the directory where this script is located
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR:~0,-1%
for %%A in ("%ROOT_DIR%") do set ROOT_DIR=%%~dpA

REM Add root directory to Python path
set PYTHONPATH=%ROOT_DIR%;%PYTHONPATH%

REM Change to root directory
cd /d "%ROOT_DIR%"

REM Run the Python backend startup script
python backend\run.py

exit /b %ERRORLEVEL%
