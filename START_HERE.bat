@echo off
setlocal
cd /d "%~dp0"
if exist "01_Project\ChurnGuide_BTech_Project\START_HERE.bat" (
    cd /d "%~dp001_Project\ChurnGuide_BTech_Project"
    call START_HERE.bat
    exit /b %errorlevel%
) else (
    echo [ERROR] Could not locate the project directory.
    echo Expected: "%~dp001_Project\ChurnGuide_BTech_Project"
    echo Please make sure you unzipped the submission archive completely before running.
    echo.
    pause
    exit /b 1
)
