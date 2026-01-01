# ollama_chat.py

import requests

OLLAMA_API_URL = "http://localhost:11434"

def list_models():
    response = requests.get(f"{OLLAMA_API_URL}/api/tags")
    response.raise_for_status()
    models = response.json().get("models", [])
    return [model["name"] for model in models]

def chat_with_model(model_name):
    print(f"\nChatting with model: {model_name}")
    print("Type 'exit' to quit.\n")
    while True:
        try:
            user_input = input("Ask anything: ")
            if user_input.strip().lower() == "exit":
                print("Exiting chat.")
                break
            payload = {
                "model": model_name,
                "prompt": user_input,
                "stream": False
            }
            response = requests.post(f"{OLLAMA_API_URL}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            print("Response:", data.get("response", "").strip())
        except KeyboardInterrupt:
            print("\nExiting chat.")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    try:
        models = list_models()
        if not models:
            print("No models found. Please pull a model using 'ollama pull <model_name>' first.")
            return
        print("Pulled Ollama models:")
        for idx, model in enumerate(models, 1):
            print(f"{idx}. {model}")
        while True:
            selected = input("Enter the name of the model to use: ").strip()
            if selected in models:
                chat_with_model(selected)
                break
            else:
                print("Invalid model name. Please select from the list above.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
