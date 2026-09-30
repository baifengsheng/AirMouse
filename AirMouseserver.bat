@echo off
cd /d "%~dp0"
set "PYTHONUTF8=1"

if not exist ".venv\Scripts\python.exe" (
    echo creating python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo failed to create .venv. Please install Python and add it to PATH.
        pause
        exit /b 1
    )
)

echo checking python dependencies...
".venv\Scripts\python.exe" -m pip install -r requirments.txt
if errorlevel 1 (
    echo failed to install python dependencies.
    pause
    exit /b 1
)

start "" https://localhost:5888
".venv\Scripts\python.exe" server.py
pause
