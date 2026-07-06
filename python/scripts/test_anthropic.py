import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.bedrock_service import BedrockService
import json

async def test_anthropic():
    svc = BedrockService()
    
    models_to_test = [
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "anthropic.claude-3-opus-20240229-v1:0",
        "apac.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    ]
    
    prompt = "What is 2+2? Reply with just the number."
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    for model_id in models_to_test:
        print(f"\n--- Testing model: {model_id} ---")
        try:
            response = svc.runtime_client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )
            print(f"✅ SUCCESS! Model {model_id} works.")
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_anthropic())
