from cryptography.fernet import Fernet
from pathlib import Path
from dotenv import load_dotenv
import pymysql, secrets, os, subprocess

print("= Setting up the Sandbox environment...")

root_password = secrets.token_urlsafe(24)
debug_password = secrets.token_urlsafe(24)
fernet_key = Fernet.generate_key().decode()
secret_key = secrets.token_hex(64)

conn = pymysql.connect(host='localhost', user='root', password='', autocommit=True)
cursor = conn.cursor()

cursor.execute(f"ALTER USER 'root'@'localhost' IDENTIFIED BY '{root_password}';")

cursor.execute("CREATE DATABASE IF NOT EXISTS Sandbox;")
cursor.execute(f"CREATE USER IF NOT EXISTS 'debug'@'localhost' IDENTIFIED BY '{debug_password}';")
cursor.execute("GRANT ALL PRIVILEGES ON Sandbox.* TO 'debug'@'localhost';")
cursor.execute("FLUSH PRIVILEGES;")

cursor.close()
conn.close()

env_content = f"""
EXEC_MODE=DEBUG

# Server Config
SERVER_NAME=localhost
SECRET_KEY={secret_key}
DB_URI="mysql+pymysql://debug:{debug_password}@localhost/Sandbox"
REDIS_URI=redis://:6379

# Mail Service
SMTP_URI=smtp.strato.de
SMPT_PORT=587
NRS_EMAIL=sandbox@growv-mail.org
NRS_PASSWORD="12#Sandbox:User/34"

# Cloudinary Config
CLOUDINARY_NAME=growv-sandbox
CLOUDINARY_API_KEY=754234632654881
CLOUDINARY_API_SECRET=iWUBKpY3SutNYFL9Cn3CHB7pI84

# Captcha Config
GOOGLE_PROJECT_ID=# your google cloud project id
GOOGLE_APPLICATION_CREDENTIALS="/path/to/growvolution.org/website/auth/google-service-key.json"
# -> Create your own key in your g-cloud project
RECAPTCHA_ID_V3=# your captcha v3
RECAPTCHA_ID_V2=# your captcha v2

# Google OAuth
GOOGLE_OAUTH_CLIENT=# you could create your own app therefore - if you like
GOOGLE_OAUTH_SECRET=# the corresponding secret if you did so

# Apple OAuth (not recommended for testing - would need a paid dev account)
APPLE_CLIENT_ID=# placeholder
APPLE_TEAM_ID=# placeholder
APPLE_KEY_ID=# placeholder

# Microsoft OAuth (can be configured via Azure - overkill for testing purposes)
MICROSOFT_CLIENT=# placeholder
MICROSOFT_SECRET=# placeholder

# Further Configuration
FERNET_KEY={fernet_key}

OPENAI_KEY=# OpenAI API Key for LLM Features - not necessary für basic functionality
"""

Path(".env").write_text(env_content, encoding="utf-8")

load_dotenv()
db_env = os.environ.copy()
db_env['FLASK_APP'] = 'db_main.py'
subprocess.run(["flask", "db", "init"], env=db_env)
subprocess.run(["flask", "db", "migrate", "-m", "Initial Migration"], env=db_env)
subprocess.run(["flask", "db", "upgrade"], env=db_env)

print(f"= Root password has been set to: {root_password}")
