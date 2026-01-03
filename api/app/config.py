from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    aws_region: str = "eu-central-1"
    athena_database: str
    athena_output_location: str

settings = Settings()