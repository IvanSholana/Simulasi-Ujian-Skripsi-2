import os
from pydantic import BaseModel
from fastapi import FastAPI
from utils.ai_agent.llm_instance import ai_response

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
  
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        ai_msg = ai_response(request.message)
        print(ai_msg)
        return {"response": ai_msg}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def root():
    return {"message": "Chat API is running"}