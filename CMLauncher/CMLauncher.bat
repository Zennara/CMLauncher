@echo off
TITLE Starting CMLauncher
setlocal

REM Set the minimum required Python version manually.
set "MIN_PYTHON_VERSION=3.13.2"

echo Checking if Python %MIN_PYTHON_VERSION% or greater is already installed...

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed. Proceeding with installation.
    goto INSTALL
)

REM Get the version number from the first line of python --version
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PY_VERSION=%%v"

REM Compare versions (basic string comparison since Python versioning aligns lexicographically)
if "%PY_VERSION%" geq "%MIN_PYTHON_VERSION%" (
    echo Python %PY_VERSION% is already installed.
    goto RUN
) else (
    echo Python %PY_VERSION% is installed, but it is not the required version.
    echo Proceeding with installation.
    goto INSTALL
)

:INSTALL
set "installer=python-%MIN_PYTHON_VERSION%-amd64.exe"
set "url=https://www.python.org/ftp/python/%MIN_PYTHON_VERSION%/%installer%"

echo Downloading Python installer...
powershell -Command "(New-Object Net.WebClient).DownloadFile('%url%', '%installer%')"

echo Installing Python...
start /wait %installer% /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 && (
    echo Installation complete.
) || (
    echo Installation failed!
    pause
    exit /b 1
)

echo Cleaning up installer...
del %installer%
echo Installation complete. Please restart the launcher.
pause
exit /b 0

:RUN
echo Starting the program...

REM Check if pythonw exists and use it, otherwise fallback to python
where pythonw >nul 2>nul
if errorlevel 1 (
    echo pythonw not found, using python instead.
    start "" python Code\main.py
) else (
    start "" pythonw Code\main.py
)

REM Ensure the installer script closes immediately
endlocal
exit /b 0
