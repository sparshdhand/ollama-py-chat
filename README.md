# Ollama Python Chat Interface

This project provides a simple command-line interface to interact with locally pulled [Ollama](https://ollama.com/) models. It allows you to list available models, select one, and ask questions in a conversational loop. The selected Ollama model processes your queries and returns responses directly in your terminal.

## Prerequisites

Before running the script, ensure you have the following installed:

*   **Python 3.x**: Ensure you have Python installed. You can check by running `python --version` or `python3 --version`.
*   **Ollama**: Download and install Ollama from [ollama.com](https://ollama.com/download).
*   **Ollama Models**: You must have at least one model pulled locally.

## Getting Started

Follow these steps to set up and run the project.

### 1. Clone the Project

Clone the repository to your local machine:

```bash
git clone https://github.com/sparshdhand/ollama-py-chat
cd ollama-py-chat
```

### 2. Create and Activate a Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

**On Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**On macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt.

### 3. Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install requests
```

### 4. Set Up Ollama

1.  Make sure Ollama is installed and running on your machine (usually reachable at `http://localhost:11434`).
2.  Ensure at least one model is pulled. For example, to pull `llama3`:

    ```bash
    ollama pull llama3
    ```

### 5. Run the Python Script

Execute the script to start the chat interface:

```bash
python ollama.py
```

## Usage

1.  **List Models:** The script will automatically fetch and list all models currently available in your Ollama instance.
2.  **Select Model:** Type the exact name of the model you wish to use from the list and press Enter.
3.  **Chat:**
    *   You will be prompted with `Ask anything:`.
    *   Type your question and press Enter.
    *   The model's response will be displayed.
4.  **Exit:** Type `exit` to quit the application.

## Troubleshooting

*   **Connection Error:** If you see an error related to connection refusal, ensure the Ollama service is running. You can typically start it by running `ollama serve` in a separate terminal window.
*   **No Models Found:** If the script reports no models, run `ollama list` in your terminal to verify you have models installed. If not, use `ollama pull <model_name>`.
*   **Invalid Model Name:** Ensure you type the model name exactly as it appears in the list.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the LICENSE file included in this repository.
