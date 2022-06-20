import os
from pydantic import BaseSettings

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


class Settings(BaseSettings):

    # Корень проекта
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    SECRET_KEY = os.getenv('SECRET_KEY')

    #postgres
    USERNAME = os.getenv('POSTGRES_USER')
    PASSWORD = os.getenv('POSTGRES_PASSWORD')
    HOST = os.getenv('POSTGRES_HOST')
    PORT = os.getenv('POSTGRES_PORT')
    DATABASE_NAME = os.getenv('POSTGRES_DB')

    REDIS_PORT: str = os.getenv('REDIS_PORT')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class DevSettings(Settings):

    REDIS_HOST: str = os.getenv('REDIS_HOST')


class TestSettings(Settings):

    REDIS_HOST: str

    class Config:
        fields ={
            "REDIS_HOST": {
                'env': 'REDIS_HOST_DEBUG'
            }
        }


def get_settings():
    environment = os.getenv('ENVIRONMENT')
    if environment=='dev':
        return get_dev_settings()
    else:
        return get_test_settings()


def get_test_settings():
    return TestSettings()


def get_dev_settings():
    return DevSettings()