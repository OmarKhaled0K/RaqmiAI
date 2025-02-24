import boto3
from src.core.config import settings
from botocore.exceptions import ClientError

class S3Adapter:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    async def upload_audio(self, file, file_name: str) -> str:
        try:
            self.client.upload_fileobj(
                file,
                settings.AWS_S3_BUCKET_NAME,
                file_name,
                ExtraArgs={'ACL': 'public-read'}
            )
            return f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_name}"
        except ClientError as e:
            raise Exception(f"S3 upload error: {str(e)}")