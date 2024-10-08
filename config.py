import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Debugging: Check if variables are loaded
print("SECRET_KEY:", os.getenv('SECRET_KEY'))
print("SQLALCHEMY_DATABASE_URI:", os.getenv('SQLALCHEMY_DATABASE_URI'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# Dictionary to hold configuration classes
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
