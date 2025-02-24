import boto3
from src.core.config import settings
import time

class PollyAdapter:
    def __init__(self):
        self.client = boto3.client(
            'polly',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    def synthesize_speech(self, text: str) -> str:
        is_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
        
        # Configure for Arabic Gulf (Neural) with Zayd
        if is_arabic:
            voice_id = 'Zayd'  # Arabic (Gulf) male neural voice
            language_code = 'ar-AE'  # Gulf Arabic
            engine = 'neural'
        else:
            # Default to English neural voice (e.g., Joanna)
            voice_id = settings.AWS_POLLY_VOICE_EN
            language_code = 'en-US'
            engine = 'neural'

        response = self.client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice_id,
            Engine=engine,
            LanguageCode=language_code
        )
        
        s3 = boto3.client('s3')
        file_name = f"response_{int(time.time())}.mp3"
        s3.put_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=file_name,
            Body=response['AudioStream'].read(),
            ACL='public-read',
            ContentType='audio/mpeg'
        )
        
        return f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_name}"