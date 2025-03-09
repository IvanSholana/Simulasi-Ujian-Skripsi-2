from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize OpenAI API key
if not os.environ.get("OPENAI_API_KEY"):
  # Note: For production, use a proper configuration management system
  # instead of hardcoding the API key
  os.environ["OPENAI_API_KEY"] = "your-api-key-here"

model = init_chat_model("gpt-4o-mini", model_provider="openai")

def ai_response(text: str) -> str:
    try:
        response = model.invoke(text)
        return response.content
    except Exception as e:
        raise Exception(f"AI model error: {str(e)}")

