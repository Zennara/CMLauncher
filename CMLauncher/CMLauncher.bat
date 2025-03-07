@echo off
TITLE Starting CMLauncher
setlocal

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
    REM Download and install Python
    set "PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe"
    set "PYTHON_INSTALLER=python_installer.exe"
    curl -o %PYTHON_INSTALLER% %PYTHON_INSTALLER_URL%
    start /wait %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1
    del %PYTHON_INSTALLER%
)

REM Run the program without opening a new console window
start /b python Code\main.py

endlocal
exit