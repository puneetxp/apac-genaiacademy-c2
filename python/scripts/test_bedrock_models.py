import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.bedrock_service import BedrockService

async def test_models():
    svc = BedrockService()
    
    models_to_test = [
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0",
        "anthropic.claude-v2:1",
        "anthropic.claude-v2",
        "amazon.titan-text-express-v1",
        "amazon.titan-text-premier-v1:0",
        "meta.llama3-8b-instruct-v1:0",
        "meta.llama3-70b-instruct-v1:0",
        "meta.llama2-13b-chat-v1",
        "mistral.mistral-7b-instruct-v0:2",
        "mistral.mixtral-8x7b-instruct-v0:1"
    ]
    
    working_models = []
    
    for model_id in models_to_test:
        print(f"\n--- Testing model: {model_id} ---")
        try:
            prompt = "What is 2+2? Reply with just the number."
            # We'll use the raw invoke_model for the test to handle differences in request formats easily, 
            # or just test the anthropic specific ones if they only use anthropic.
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": prompt}]
            } if "claude-3" in model_id else {
                "prompt": f"\\n\\nHuman: {prompt}\\n\\nAssistant:",
                "max_tokens_to_sample": 10
            } if "claude" in model_id else {
                "inputText": prompt,
                "textGenerationConfig": {"maxTokenCount": 10}
            } if "titan" in model_id else {
                "prompt": prompt,
                "max_gen_len": 10
            }
            
            import json
            response = svc.runtime_client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )
            print(f"✅ SUCCESS! Model {model_id} works.")
            working_models.append(model_id)
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            
    print("\n\nWORKING MODELS:", working_models)

if __name__ == "__main__":
    asyncio.run(test_models())
