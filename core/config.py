import os

from dotenv import load_dotenv

load_dotenv(
    dotenv_path=".env"
)

DJANGO_SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DEBUG')
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS').split(',') if host]

DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')