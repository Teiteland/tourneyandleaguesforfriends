import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE_URI = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_URI') or 'sqlite:///gaming_liga.db'
