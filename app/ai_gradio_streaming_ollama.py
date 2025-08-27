import requests
import json
import os

BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

explanation_levels = {
    1: "Like I'm 5 years old",
    2: "Like I'm 10 years old",
    3: "Like a high school student",
    4: "Like a college student",
    5: "Like an experted in the field"
}

def get_ai_tutor_streaming_response(user_prompt, explanation_level_value):
    try:
        level_description = explanation_levels.get(explanation_level_value, "clearly and concisely")
        system_prompt = f"You are an AI tutor with high experience explaning and teaching. Explain the topic in the follow level: {level_description}"
        
        url = f"{BASE_URL}/api/chat"
        
        data = {
            "model": "llama3.1",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ],
            "stream": True,
            "options": {
                "temperature": 0.7
            }
        }
        
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()
        
        full_response = ""
        
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    
                    if 'message' in chunk and 'content' in chunk['message']:
                        content = chunk['message']['content']
                        full_response += content
                        yield full_response 
                    
                    if chunk.get('done', False):
                        break
                        
                except json.JSONDecodeError:
                    continue

    except requests.exceptions.ConnectionError:
        yield "Error: Ollama connection failed"
    except requests.exceptions.RequestException as e:
        yield f"Request error: {e}"
    except Exception as e:
        yield f"Unexpected error: {e}"