import os
import base64
import json
from fastapi import FastAPI, Request, HTTPException
from google.cloud import aiplatform
import requests
from google.auth import default
from google.auth.transport.requests import Request as AuthRequest

app = FastAPI()

PROJECT_ID = "demo4events10"
LOCATION = "us-central1"
REASONING_ENGINE_ID = "5328541761214087168"

# Initialize AI Platform
aiplatform.init(project=PROJECT_ID, location=LOCATION)
resource_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}"

try:
    engine = aiplatform.ReasoningEngine(resource_name)
except Exception as e:
    print(f"Error initializing Reasoning Engine: {e}")
    engine = None

SECRET_TOKEN = os.environ.get("CHAT_SECRET_TOKEN", "my_demo_secret")

def get_iam_token():
    # Request token with Chat scope
    credentials, project = default(scopes=["https://www.googleapis.com/auth/chat.messages"])
    auth_request = AuthRequest()
    credentials.refresh(auth_request)
    return credentials.token

@app.post("/")
async def chat_webhook(request: Request):
    # Verify secret token
    secret = request.query_params.get("secret")
    if secret != SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")

    body = await request.json()
    print(f"Received body: {body}")

    # Decode Pub/Sub message
    message_data = body.get("message", {}).get("data")
    if not message_data:
        return {"status": "No data in message"}

    try:
        decoded_data = base64.b64decode(message_data).decode("utf-8")
        event = json.loads(decoded_data)
        print(f"Decoded event: {event}")
    except Exception as e:
        print(f"Error decoding message: {e}")
        return {"status": "Error decoding message"}

    if event.get("type") != "MESSAGE":
        return {"status": "Not a message event"}

    message = event.get("message", {})
    text = message.get("text", "")
    space_name = event.get("space", {}).get("name", "")
    thread_name = message.get("thread", {}).get("name", "")

    if not space_name:
        return {"status": "No space name in event"}

    # Strip mention if present
    query_text = text
    if text.startswith("@"):
        parts = text.split(" ", 1)
        if len(parts) > 1:
            query_text = parts[1]
        else:
            query_text = ""

    if not query_text:
        return {"status": "Empty query"}

    # Call Vertex AI Reasoning Engine
    agent_response = "No response from agent."
    try:
        if not engine:
             agent_response = "Reasoning Engine not initialized."
        else:
            result = engine.query(query=query_text)
            if isinstance(result, str):
                agent_response = result
            elif isinstance(result, dict):
                agent_response = result.get("response", str(result))
            else:
                agent_response = str(result)

    except Exception as e:
        print(f"Error calling agent: {e}")
        agent_response = f"Error calling agent: {str(e)}"

    # Call Google Chat API to post response
    try:
        token = get_iam_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        chat_url = f"https://chat.googleapis.com/v1/{space_name}/messages"
        
        payload = {
            "text": agent_response
        }
        if thread_name:
            payload["thread"] = {"name": thread_name}
            
        print(f"Posting to Chat: {chat_url} with payload: {payload}")
        response = requests.post(chat_url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Chat response: {response.json()}")
        
        return {"status": "Reply posted"}

    except Exception as e:
        print(f"Error posting to Chat: {e}")
        return {"status": f"Error posting to Chat: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
