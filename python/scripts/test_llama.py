import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.bedrock_service import BedrockService
import json

async def test_llama():
    svc = BedrockService()
    
    model_id = "meta.llama3-70b-instruct-v1:0"
    
    prompt = "What is 2+2? Reply with just the number."
    
    formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    
    body = {
        "prompt": formatted_prompt,
        "max_gen_len": 100,
        "temperature": 0.1
    }
    
    print("Invoking...")
    
    response = svc.runtime_client.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )
    
    response_body = json.loads(response.get('body').read())
    print(response_body)

if __name__ == "__main__":
    asyncio.run(test_llama())
