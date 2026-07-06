import os
import sys

for key in list(os.environ.keys()):
    if key.startswith('AWS_'):
        del os.environ[key]

import boto3
import json

client = boto3.client(
    service_name="bedrock-runtime",
    region_name="ap-south-1",
    aws_access_key_id="YOUR_AWS_ACCESS_KEY_ID",
    aws_secret_access_key="YOUR_AWS_SECRET_ACCESS_KEY",
    aws_session_token=None
)

response = client.invoke_model(
    modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ]
    })
)

result = json.loads(response["body"].read())
print("API Key worked!", result["content"][0]["text"])
