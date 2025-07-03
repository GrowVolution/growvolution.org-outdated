@echo off
setlocal EnableDelayedExpansion

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo - Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

echo = Running as administrator.

set PYTHON_VERSION=3.13.5
set MARIADB_VERSION=11.8.2
set REDIS_VERSION=8.0.2

echo = Checking for Python installation...
where python >nul 2>&1
if errorlevel 1 (
    echo - Installing Python %PYTHON_VERSION%...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe -OutFile python-installer.exe"
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python-installer.exe
) else (
    echo - Python already installed.
)

echo.
echo = Creating virtual environment...
python -m venv .venv

echo.
echo = Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo = Upgrading pip and installing requirements...
pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo ! WARNING: requirements.txt not found.
)

echo.
echo = Checking for MariaDB installation...
where mariadb >nul 2>&1
if errorlevel 1 (
    echo - Installing MariaDB %MARIADB_VERSION%...
    powershell -Command "Invoke-WebRequest -Uri https://downloads.mariadb.com/MariaDB/mariadb-%MARIADB_VERSION%/winx64-packages/mariadb-%MARIADB_VERSION%-winx64.msi -OutFile mariadb-installer.msi"
    start /wait msiexec /i mariadb-installer.msi /quiet /qn INSTALLDIR="C:\MariaDB" ADDLOCAL=ALL
    del mariadb-installer.msi
) else (
    echo - MariaDB already installed.
)

where redis-server >nul 2>&1
if errorlevel 1 (
    echo [INFO] Redis not found. Installing version %REDIS_VERSION%...
    set ZIP_URL=https://github.com/redis-windows/redis-windows/releases/download/%REDIS_VERSION%/Redis-%REDIS_VERSION%-Windows-x64-msys2.zip
    powershell -Command "Invoke-WebRequest -Uri %ZIP_URL% -OutFile redis-%REDIS_VERSION%.zip"
    powershell -Command "Expand-Archive redis-%REDIS_VERSION%.zip -DestinationPath C:\Program Files\Redis"
    set PATH="C:\Program Files\Redis\Redis-%REDIS_VERSION%-Windows-x64-msys2";%PATH%
    del redis-%REDIS_VERSION%.zip
    echo [OK] Redis %REDIS_VERSION% installed at C:\Program Files\Redis.
) else (
    echo [OK] Redis already installed.
)

echo.
python setup.py

echo.
echo = Setup complete! - run 'python main.py' to start the application.
pause
