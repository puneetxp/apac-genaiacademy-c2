import sys
sys.path.append('..')
from app.services.bedrock_service import BedrockService
import json

svc = BedrockService()
print(f"Model ID: {svc.claude_model_id}")
print(f"Region: us-east-1")

response = svc._invoke_claude("What is 2+2? Reply with just the number.", max_tokens=10)
print(f"✅ BedrockService._invoke_claude works! Answer: {response}")
