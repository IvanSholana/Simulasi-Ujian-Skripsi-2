from app.utils.ai_agent.llm_instance import LLMInstance
from app.static.prompts.expand_query import expansion_prompt
import json

def expand_query(main_query:str):
    agent = LLMInstance()
    expanded_query = agent.invoke(expansion_prompt.format(query=main_query))
    try:
        expanded_json = json.loads(expanded_query)
        # Jika expanded_json adalah dictionary dengan array/list di dalamnya
        if isinstance(expanded_json, dict):
            # Ambil values dari dictionary dan gabungkan jika ada multiple keys
            expanded_list = []
            for value in expanded_json.values():
                if isinstance(value, list):
                    expanded_list.extend(value)
                else:
                    expanded_list.append(value)
            return expanded_list
        # Jika expanded_json sudah berupa list
        elif isinstance(expanded_json, list):
            return expanded_json
        else:
            return [expanded_json]
    except json.JSONDecodeError:
        return ["Error: Failed to parse response as JSON"]
