from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

class LLMInstance:
  def __init__(self, model_name="gpt-4o-mini", model_provider="openai", api_key=None):
    load_dotenv()
    
    # Set API key from parameter or environment variable
    if api_key:
      os.environ["OPENAI_API_KEY"] = api_key
    elif not os.environ.get("OPENAI_API_KEY"):
      # Note: For production, use a proper configuration management system
      # instead of hardcoding the API key
      os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    
    self.model = init_chat_model(model_name, model_provider=model_provider)
  
  def invoke(self, prompt, **kwargs):
    try:
      if kwargs:
        response = self.model.invoke(prompt.format(**kwargs))
      else:
        response = self.model.invoke(prompt)
      return response.content
    except Exception as e:
      raise Exception(f"AI model error: {str(e)}")
    
    