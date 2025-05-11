from flask import Flask, Blueprint, render_template, request, redirect, session, flash, make_response, abort
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from pathlib import Path
from importlib import import_module
from smtplib import SMTP, SMTPException, SMTPResponseException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from threading import Thread
from debugger import log, debug_msg
from urllib.parse import urlencode
from markupsafe import Markup
import subprocess, warnings, random, string,\
    time, os, secrets, requests, jwt, json, \
    cloudinary as cloudinary_, cloudinary.uploader as cloudinary_uploader, \
    cloudinary.api as cloudinary_api


ROOT_PATH = Path(__file__).parent

POST_METHOD = ['POST']
ALL_METHODS = ['GET', 'POST']


def back_home():
    return redirect('/')


def back_to_login():
    return redirect('/login')


def random_code(length=6):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
