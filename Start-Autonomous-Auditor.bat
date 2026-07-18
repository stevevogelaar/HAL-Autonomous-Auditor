@echo off
REM HAL Autonomous Auditor launcher
REM Runs an autonomous security audit against a target directory.

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

set PYTHON=C:\Users\Steve Vogelaar\AppData\Local\Programs\Python\Python312\python.exe

echo.
echo ============================================
echo   HAL Autonomous Auditor
echo ============================================
echo.
echo This will review the sample_code directory and generate a report.
echo.

"%PYTHON%" autonomous_auditor.py data\sample_code --name sample_code --model gemma4:e2b

if %errorlevel% neq 0 (
    echo.
    echo Auditor exited with an error.
    pause
)
