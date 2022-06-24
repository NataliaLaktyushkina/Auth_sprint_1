import os
from pydantic import BaseSettings

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


class Settings(BaseSettings):

    PROJECT_NAME: str = os.getenv('PROJECT_NAME', 'auth_api')
    # Корень проекта
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    SERVICE_URL: str = os.getenv("SERVICE_URL")
    URL_API_V1: str = os.getenv("URL_API_V1")

    REDIS_PORT: str = os.getenv('REDIS_PORT')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class DevSettings(Settings):

    REDIS_HOST: str = os.getenv('REDIS_HOST')


class PromSettings(Settings):

    REDIS_HOST: str

    class Config:
        fields = {
            "REDIS_HOST": {
                'env': 'REDIS_HOST_DEBUG'
            }
        }


def get_settings():
    environment = os.getenv('ENVIRONMENT')
    if environment == 'prom':
        return get_prom_settings()
    else:
        return get_dev_settings()


def get_prom_settings():
    return PromSettings()


def get_dev_settings():
    return DevSettings()
