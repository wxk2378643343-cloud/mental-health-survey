import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mh-survey-secret-2024')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, '..', 'database', 'mh_survey.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRE_HOURS = 24
