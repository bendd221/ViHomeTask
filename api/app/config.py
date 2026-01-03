from pydantic_settings import BaseSettings

from dotenv import load_dotenv
load_dotenv('api/app/.env', override=True) #For testings

class Settings(BaseSettings):
    aws_region: str = "eu-central-1"
    athena_database: str
    athena_output_location: str

settings = Settings()