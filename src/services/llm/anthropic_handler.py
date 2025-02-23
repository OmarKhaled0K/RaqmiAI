import boto3
from src.core.config import settings

class ClaudeHandler:
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    def generate_response(self, text: str) -> str:
        system_prompt_ar = "You are a helpful AI assistant. Respond in Arabic."
        system_prompt_en = "You are a helpful AI assistant. Respond in English."
        
        is_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
        system_prompt = system_prompt_ar if is_arabic else system_prompt_en

        response = self.client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body={
                "messages": [{"role": "user", "content": text}],
                "system": system_prompt,
                "max_tokens": 1000,
                "temperature": 0.5
            }
        )
        
        return response['body']['content'][0]['text']