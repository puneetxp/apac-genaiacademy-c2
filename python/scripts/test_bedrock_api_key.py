import asyncio
import os
import sys
import boto3
import json
from botocore.config import Config

async def test_bedrock_api():
    # BedrockAPIKey-g28r-at-339713064684:KptDfBnXg8ugVx0Hqm8CDIPsbXU4KTcmHWc2ZFl3ofS6sRQXXzi2+XjzsRI=
    aws_access_key_id = "BedrockAPIKey-g28r-at-339713064684"
    aws_secret_access_key = "KptDfBnXg8ugVx0Hqm8CDIPsbXU4KTcmHWc2ZFl3ofS6sRQXXzi2+XjzsRI="
    
    try:
        # Some proxy environments use AWS signature v4 locally
        my_config = Config(
            region_name = 'ap-south-1',
            signature_version = 's3v4',
        )
        
        # Test 1: use as proxy endpoint
        # There's a common proxy `bedrock-proxy` for this hackathon
        proxy_endpoints = [
            None,
            "https://bedrock.buildon.aws",
            "https://api.bedrock.buildon.aws/v1"
        ]
        
        prompt = "test"
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": prompt}]
        }

        for ep in proxy_endpoints:
            print(f"\n--- Testing Endpoint: {ep} ---")
            try:
                client = boto3.client(
                    'bedrock-runtime',
                    endpoint_url=ep,
                    region_name='us-east-1', # Buildon proxies often use us-east-1
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key
                )
                response = client.invoke_model(
                    modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(body)
                )
                print("SUCCESS with 3.5 Sonnet!")
                return
            except Exception as e:
                print(f"FAILED: {e}")
                
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_bedrock_api())
