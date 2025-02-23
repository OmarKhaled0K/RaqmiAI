from pydantic_settings import BaseSettings, SettingsConfigDict
import os
class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Voice Chat"
    VERSION: str = "0.1.0"
    ENV: str = "development"
    
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-west-2"


    AWS_S3_BUCKET_NAME: str = "ai-voice-chat-bucket"
    AWS_TRANSCRIBE_LANGUAGE: str = "auto"
    AWS_POLLY_VOICE_EN: str = "Joanna"
    AWS_POLLY_VOICE_AR: str = "Zeina"

    LOG_LEVEL: str = "INFO"
    LOGGER_NAME: str = "ai-voice-chat"
    LOGS_DIR = os.path.join(os.getcwd(),"logs")
    LOG_FILE_PATH = os.getenv(
        "LOG_FILE_PATH", os.path.join(LOGS_DIR, "logs.log"))
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()