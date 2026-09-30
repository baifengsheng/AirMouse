@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHON_EXE="

rem Optional override for portable or non-standard Python installations.
if defined AIRMOUSE_PYTHON (
    if exist "%AIRMOUSE_PYTHON%" set "PYTHON_EXE=%AIRMOUSE_PYTHON%"
)

rem Prefer the Windows Python Launcher when it is available.
if not defined PYTHON_EXE (
    where py >nul 2>&1
    if not errorlevel 1 (
        for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
    )
)

rem Fall back to python.exe on PATH.
if not defined PYTHON_EXE (
    where python >nul 2>&1
    if not errorlevel 1 (
        for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
    )
)

rem Check the default per-user and system installation directories.
if not defined PYTHON_EXE (
    for /d %%D in ("%LocalAppData%\Python\pythoncore-*") do if exist "%%~fD\python.exe" if not defined PYTHON_EXE set "PYTHON_EXE=%%~fD\python.exe"
)
if not defined PYTHON_EXE (
    for /d %%D in ("%LocalAppData%\Programs\Python\Python*") do if exist "%%~fD\python.exe" if not defined PYTHON_EXE set "PYTHON_EXE=%%~fD\python.exe"
)
if not defined PYTHON_EXE (
    for /d %%D in ("%ProgramFiles%\Python*") do if exist "%%~fD\python.exe" if not defined PYTHON_EXE set "PYTHON_EXE=%%~fD\python.exe"
)
if not defined PYTHON_EXE if defined ProgramFiles(x86) (
    for /d %%D in ("%ProgramFiles(x86)%\Python*") do if exist "%%~fD\python.exe" if not defined PYTHON_EXE set "PYTHON_EXE=%%~fD\python.exe"
)

if not defined PYTHON_EXE (
    echo ERROR: Python 3.11 or newer was not found.
    echo Install Python from https://www.python.org/downloads/windows/
    if not defined AIRMOUSE_NO_PAUSE pause
    exit /b 1
)

"%PYTHON_EXE%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 (
    echo ERROR: AirMouse requires Python 3.11 or newer.
    echo Detected interpreter: "%PYTHON_EXE%"
    if not defined AIRMOUSE_NO_PAUSE pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    "%PYTHON_EXE%" -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create .venv.
        if not defined AIRMOUSE_NO_PAUSE pause
        exit /b 1
    )
    ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --upgrade pip
    if errorlevel 1 (
        echo ERROR: Failed to update pip.
        if not defined AIRMOUSE_NO_PAUSE pause
        exit /b 1
    )
)

echo Checking Python dependencies...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies.
    if not defined AIRMOUSE_NO_PAUSE pause
    exit /b 1
)

echo Verifying AirMouse installation...
".venv\Scripts\python.exe" verify_install.py
if errorlevel 1 (
    echo ERROR: AirMouse installation verification failed.
    if not defined AIRMOUSE_NO_PAUSE pause
    exit /b 1
)

if not defined AIRMOUSE_NO_BROWSER (
    start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'https://localhost:5888'"
)

".venv\Scripts\python.exe" server.py
set "SERVER_EXIT=%ERRORLEVEL%"
if not "%SERVER_EXIT%"=="0" echo AirMouse server exited with code %SERVER_EXIT%.
if not defined AIRMOUSE_NO_PAUSE pause
exit /b %SERVER_EXIT%
