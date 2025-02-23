from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Voice Chat"
    VERSION: str = "0.1.0"
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-west-2"


    AWS_S3_BUCKET_NAME: str = "ai-voice-chat-bucket"
    AWS_TRANSCRIBE_LANGUAGE: str = "auto"
    AWS_POLLY_VOICE_EN: str = "Joanna"
    AWS_POLLY_VOICE_AR: str = "Zeina"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()