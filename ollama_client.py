import requests
import json

OLLAMA_API_URL = "http://localhost:11434"

class OllamaClient:
    def __init__(self, base_url=OLLAMA_API_URL):
        self.base_url = base_url

    def list_models(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        except requests.exceptions.RequestException as e:
            print(f"Error listing models: {e}")
            return []

    def chat(self, model, messages, stream=True):
        """
        Sends a chat request to Ollama.
        messages: list of dicts {'role': '...', 'content': '...'}
        Yields chunks of content if stream=True.
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }

        try:
            with requests.post(url, json=payload, stream=stream) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        if "message" in data:
                            yield data["message"]["content"]
                        if data.get("done", False):
                            break
        except requests.exceptions.RequestException as e:
            yield f"Error: {str(e)}"
