#!/bin/bash

set -e

if [[ "$EUID" -ne 0 ]]; then
    echo "- Script is not running as root. Re-launching with sudo..."
    exec sudo "$0" "$@"
    exit
fi

echo "= Running as root."

PYTHON_VERSION="3.13.5"
MARIADB_VERSION="11.8.2"
REDIS_VERSION="8.0"

echo "= Checking for Python..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "- Python not found. Installing Python $PYTHON_VERSION..."
    OS=$(uname)
    if [[ "$OS" == "Darwin" ]]; then
        if ! command -v brew >/dev/null 2>&1; then
            echo "- Homebrew not found. Installing Homebrew first..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python
    elif [[ -f /etc/debian_version ]]; then
        sudo apt update
        sudo apt install -y wget build-essential libssl-dev zlib1g-dev \
        libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev \
        libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev

        wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
        tar -xf Python-$PYTHON_VERSION.tgz
        cd Python-$PYTHON_VERSION
        ./configure --enable-optimizations
        make -j$(nproc)
        sudo make altinstall
        cd ..
        rm -rf Python-$PYTHON_VERSION*
    else
        echo "! Unsupported OS. Please install Python manually."
        exit 1
    fi
else
    echo "- Python is already installed."
fi

echo
echo "= Creating virtual environment..."
python3 -m venv .venv

echo
echo "= Activating virtual environment..."
source .venv/bin/activate

echo
echo "= Upgrading pip and installing requirements..."
pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "! WARNING: requirements.txt not found."
fi

echo
echo "= Checking for MariaDB..."
if ! command -v mariadbd >/dev/null 2>&1; then
    echo "- MariaDB not found. Installing MariaDB $MARIADB_VERSION..."
    if [[ "$OS" == "Darwin" ]]; then
        brew install mariadb
    elif [[ -f /etc/debian_version ]]; then
        sudo apt install -y mariadb-server
    else
        echo "! Unsupported OS for MariaDB installation."
        exit 1
    fi
else
    echo "- MariaDB is already installed."
fi

echo "= Checking for redis-server..."
if ! command -v redis-server >/dev/null 2>&1; then
    echo "- Redis not found. Installing version $REDIS_VERSION..."
    OS=$(uname)
    if [[ "$OS" == "Darwin" ]]; then
        brew install redis
    elif [[ -f /etc/debian_version ]]; then
        sudo apt update
        sudo apt install -y curl build-essential tcl
        curl -O http://download.redis.io/releases/redis-$REDIS_VERSION.tar.gz
        tar xzf redis-$REDIS_VERSION.tar.gz
        cd redis-$REDIS_VERSION
        make distclean || true
        make -j$(nproc)
        sudo make install
        cd ..
        rm -rf redis-$REDIS_VERSION*
    else
        echo "! Unsupported OS. Install Redis manually."
        exit 1
    fi
    echo "[OK] Redis $REDIS_VERSION installed."
else
    echo "[OK] Redis already present."
fi

echo
python setup.py

echo
echo "= Setup complete! - run 'python main.py' to start the application."
