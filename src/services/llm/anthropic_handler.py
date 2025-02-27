import json
import os
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
        
        # Load context file
        self.airport_context = self._load_context_file()

    def _load_context_file(self) -> str:
        """Load and return the context from the text file"""
        try:
            context_path = os.path.join(
                "src/services/llm/prompts/context/", 
                "airport.txt"
            )
            with open(context_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise RuntimeError(f"Context file not found at {context_path}")
        except Exception as e:
            raise RuntimeError(f"Error reading context file: {str(e)}")

    def generate_response(self, text: str, **kwargs) -> str:
        # Format prompts with context
        system_prompt = Prompts.COMPANY_SYSTEM_PROMPT.format(
            context=self.airport_context
        )
        user_prompt = Prompts.USER_PROMPT.format(record_text=text)

        # Create the request body
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

        # Get response from Claude
        response = self.client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=body_bytes
        )
        
        # Parse and return response
        response_body = json.loads(response['body'].read().decode('utf-8'))
        return response_body['content'][0]['text']