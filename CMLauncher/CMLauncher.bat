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

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed. Installing pip...
    python -m ensurepip --default-pip
)

REM Set up virtual environment
if not exist Code\.venv (
    python -m venv Code\.venv
)

REM Activate virtual environment
call Code\.venv\Scripts\activate

REM Install required dependencies
if exist requirements.txt (
    pip install -r requirements.txt
)

REM Run the program without opening a new console window
start /b pythonw Code\main.py

REM Deactivate virtual environment
call Code\.venv\Scripts\deactivate

endlocal
exit