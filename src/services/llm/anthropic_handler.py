import json
import boto3
from src.core.config import settings
from .prompts.base_prompts import Prompts
class ClaudeHandler:
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    def generate_response(self, text: str,**kwargs) -> str:
        system_prompt = Prompts.COMPANY_SYSTEM_PROMPT.format(company_name=settings.COMPANY_NAME,
                                                      industry = settings.INDUSTRY,
                                                      products_services=settings.PRODUCTS_SERVICES,
                                                      target_audience=settings.TARGET_AUDIENCE,
                                                      location=settings.LOCATION)
        user_prompt = Prompts.USER_PROMPT.format(record_text=text)

        # Create the proper request body format
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": user_prompt
                }]
            }],
            "system": system_prompt,
            "max_tokens": 250,
            "temperature": 0
        }

        # Convert to JSON bytes
        body_bytes = json.dumps(body).encode('utf-8')

        response = self.client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=body_bytes
        )
        
        # Parse the response properly
        response_body = json.loads(response['body'].read().decode('utf-8'))
        return response_body['content'][0]['text']