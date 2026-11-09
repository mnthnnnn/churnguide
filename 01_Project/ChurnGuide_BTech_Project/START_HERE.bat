@echo off
setlocal enabledelayedexpansion
title ChurnGuide - AI Customer Analytics Launcher

echo ======================================================================
echo          AI Customer Analytics ^& Churn Prediction System
echo                       One-Click Launcher
echo ======================================================================
echo.

cd /d "%~dp0"
echo [INIT] Project Root: %cd%

:: Set clean writable Matplotlib config directory to prevent font cache warnings
set "MPLCONFIGDIR=%TEMP%\matplotlib_churnguide"
if not exist "%TEMP%\matplotlib_churnguide" mkdir "%TEMP%\matplotlib_churnguide" >nul 2>&1

:: Check for OneDrive synced folder
echo %cd% | findstr /i "OneDrive" >nul
if %errorlevel% equ 0 (
    echo [WARNING] Project is inside a OneDrive synced folder.
    echo           If you encounter file locks, pause sync or move to C:\projects.
    echo.
)

set "PYTHON_CMD="
set "BASE_PYTHON="

:: =========================================================================
:: PHASE 1: Find a Python that ALREADY has required packages ready
:: =========================================================================
echo [SEARCH] Detecting Python environment with required dependencies...

:: 1. Check local virtual environment (.venv)
if exist ".venv\Scripts\python.exe" call :test_ready_python "%~dp0.venv\Scripts\python.exe"
if defined PYTHON_CMD goto :found_ready_python

:: 2. Check standard Windows user installations (Python 3.10 - 3.14)
for /d %%d in ("%LocalAppData%\Programs\Python\Python3*") do (
    if not defined PYTHON_CMD if exist "%%d\python.exe" call :test_ready_python "%%d\python.exe"
)
if defined PYTHON_CMD goto :found_ready_python

:: 3. Check 64-bit Program Files
for /d %%d in ("C:\Program Files\Python3*") do (
    if not defined PYTHON_CMD if exist "%%d\python.exe" call :test_ready_python "%%d\python.exe"
)
if defined PYTHON_CMD goto :found_ready_python

:: 4. Check python on PATH (filtering out WindowsApps dummy alias)
where.exe python >"%TEMP%\churnguide_py_list.txt" 2>nul
if exist "%TEMP%\churnguide_py_list.txt" (
    for /f "usebackq delims=" %%i in ("%TEMP%\churnguide_py_list.txt") do (
        if not defined PYTHON_CMD (
            echo %%i | findstr /i "WindowsApps" >nul
            if errorlevel 1 call :test_ready_python "%%i"
        )
    )
    del "%TEMP%\churnguide_py_list.txt" >nul 2>&1
)
if defined PYTHON_CMD goto :found_ready_python

:: 5. Check Windows py launcher
where.exe py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import pandas, flask, sklearn, joblib, matplotlib" >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=py -3"
        goto :found_ready_python
    )
)

goto :find_base_python

:found_ready_python
echo [OK] Verified Python environment: !PYTHON_CMD!
echo [OK] All dependencies are ready.
goto :verify_models

:: =========================================================================
:: PHASE 2: Find a base Python interpreter (to install packages into)
:: =========================================================================
:find_base_python
echo [INFO] Ready environment not found. Locating base Python interpreter...

for /d %%d in ("%LocalAppData%\Programs\Python\Python3*") do (
    if not defined BASE_PYTHON if exist "%%d\python.exe" call :test_base_python "%%d\python.exe"
)
if defined BASE_PYTHON goto :install_deps

for /d %%d in ("C:\Program Files\Python3*") do (
    if not defined BASE_PYTHON if exist "%%d\python.exe" call :test_base_python "%%d\python.exe"
)
if defined BASE_PYTHON goto :install_deps

where.exe python >"%TEMP%\churnguide_py_list.txt" 2>nul
if exist "%TEMP%\churnguide_py_list.txt" (
    for /f "usebackq delims=" %%i in ("%TEMP%\churnguide_py_list.txt") do (
        if not defined BASE_PYTHON (
            echo %%i | findstr /i "WindowsApps" >nul
            if errorlevel 1 call :test_base_python "%%i"
        )
    )
    del "%TEMP%\churnguide_py_list.txt" >nul 2>&1
)
if defined BASE_PYTHON goto :install_deps

where.exe py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        set "BASE_PYTHON=py -3"
        goto :install_deps
    )
)

:: =========================================================================
:: PHASE 3: Auto-install Python 3.12 if not present on this machine
:: =========================================================================
echo.
echo ======================================================================
echo  [SETUP] Python is not installed on this computer.
echo  [SETUP] Automatically installing official Python 3.12 now...
echo ======================================================================
echo.

where.exe winget >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Installing Python 3.12 via Windows Package Manager...
    winget install --id Python.Python.3.12 --exact --silent --accept-source-agreements --accept-package-agreements
    for /d %%d in ("%LocalAppData%\Programs\Python\Python312*") do (
        if exist "%%d\python.exe" set "BASE_PYTHON="%%d\python.exe""
    )
    if not defined BASE_PYTHON (
        if exist "C:\Program Files\Python312\python.exe" set "BASE_PYTHON="C:\Program Files\Python312\python.exe""
    )
)
if defined BASE_PYTHON goto :install_deps

echo [INFO] Downloading official Python 3.12 64-bit installer from python.org...
set "PY_INSTALLER=%TEMP%\python_312_setup.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe', '%TEMP%\python_312_setup.exe')"
if exist "%TEMP%\python_312_setup.exe" (
    echo [INFO] Performing silent background installation...
    "%TEMP%\python_312_setup.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_pip=1 TargetDir="%LocalAppData%\Programs\Python\Python312"
    del "%TEMP%\python_312_setup.exe" >nul 2>&1
    if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
        set "BASE_PYTHON="%LocalAppData%\Programs\Python\Python312\python.exe""
    )
)
if defined BASE_PYTHON goto :install_deps

echo.
echo [ERROR] Could not install Python automatically.
echo Please download and install Python 3.10+ from: https://www.python.org/downloads/
echo Check 'Add python.exe to PATH' during installation.
echo.
pause
exit /b 1

:: =========================================================================
:: PHASE 4: Create local virtual environment and install dependencies
:: =========================================================================
:install_deps
echo [OK] Using Python base: !BASE_PYTHON!
echo [INFO] Creating clean local environment and installing required packages...
echo        This only runs once on initial setup (takes ~30-60 seconds)...
echo.

!BASE_PYTHON! -m venv .venv
if exist ".venv\Scripts\python.exe" (
    set "EXEC_PYTHON="%~dp0.venv\Scripts\python.exe""
) else (
    set "EXEC_PYTHON=!BASE_PYTHON!"
)

!EXEC_PYTHON! -m pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo [ERROR] Failed to install required packages.
    echo Please check your internet connection and try running again.
    pause
    exit /b 1
)

set "PYTHON_CMD=!EXEC_PYTHON!"
echo [OK] All dependencies successfully prepared!

:: =========================================================================
:: PHASE 5: Verify pre-trained business models
:: =========================================================================
:verify_models
if exist "projects\telecom_public_demo\pipeline.joblib" (
    echo [OK] Pre-trained enterprise models verified.
    goto :launch_server
)

echo [INFO] Initializing enterprise business models...
"!PYTHON_CMD!" scripts\initialize_demo_projects.py
if !errorlevel! neq 0 (
    echo [ERROR] Model initialization failed.
    pause
    exit /b 1
)
echo [OK] Enterprise business models initialized successfully.

:: =========================================================================
:: PHASE 6: Launch application server
:: =========================================================================
:launch_server
echo.
echo ======================================================================
echo  [SERVER] Starting ChurnGuide production server at http://127.0.0.1:5000
echo  [BROWSER] Opening dashboard in your default browser automatically...
echo  [CONTROL] Press Ctrl+C in this terminal window anytime to stop the server.
echo ======================================================================
echo.

"!PYTHON_CMD!" app.py

if !errorlevel! neq 0 (
    echo.
    echo [ERROR] The application server terminated with code !errorlevel!.
    echo If port 5000 was busy, the server automatically attempted higher ports.
    pause
)
exit /b 0

:: =========================================================================
:: Subroutines
:: =========================================================================
:test_ready_python
set "cand=%~1"
if not exist "%cand%" exit /b 0
"%cand%" -c "import pandas, flask, sklearn, joblib, matplotlib" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD="%cand%""
)
exit /b 0

:test_base_python
set "cand=%~1"
if not exist "%cand%" exit /b 0
"%cand%" -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "BASE_PYTHON="%cand%""
)
exit /b 0
