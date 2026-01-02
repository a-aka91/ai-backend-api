# AI Agent Project

This project implements an intelligent AI Agent using Python and OpenAI's GPT models. It features a versatile agent capable of tool use (function calling) for retrieving real-time information such as weather and internet search results. The project exposes this functionality through both a Command Line Interface (CLI) and a streaming FastAPI web server.

## Features

- **OpenAI Integration**: Powered by `gpt-4o-mini` (configurable) for natural language processing.
- **Tool Calling capabilities**:
  - **`get_current_time`**: Retrieves the current server date and time.
  - **`get_weather`**: Provides weather updates (mock data for demo purposes) for locations like Rabat, London, and Paris.
  - **`search_internet`**: Performs real-time internet searches using DuckDuckGo to answer questions with up-to-date information.
- **Dual Interface**:
  - **CLI**: Interactive terminal-based chat.
  - **API**: FastAPI backend with **Streaming Response** support for real-time token generation.

## Prerequisites

- Python 3.8+
- An OpenAI API Key

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory.

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Mac/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**:
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-your-api-key-here
   ```

## Usage

### 1. Command Line Interface (CLI)
You can run the agent directly in your terminal to chat with it.

```bash
python agent_class.py
```
Type `exit` or `quit` to stop the session.

### 2. API Server
Start the FastAPI server to expose the chat endpoint.

```bash
uvicorn api:app --reload
```
The server will start at `http://127.0.0.1:8000`.

### API Endpoints

- **POST `/chat`**
  - **Body**: `{"prompt": "Your message here"}`
  - **Response**: Returns a text stream of the AI's response.

  **Example Request (using curl):**
  ```bash
  curl -X POST "http://127.0.0.1:8000/chat" \
       -H "Content-Type: application/json" \
       -d "{\"prompt\": \"What is the weather in Paris?\"}"
  ```

## Project Structure

- **`agent_class.py`**: Contains the `AIAgent` class, defining the agent's memory, tools, and interaction logic with OpenAI. Also handles the CLI execution loop.
- **`api.py`**: Functional FastAPI application that imports the agent and wraps it in a streaming HTTP endpoint.
- **`requirements.txt`**: List of Python dependencies required for the project.
- **`tuto/`**: A directory containing various tutorial scripts, examples (RAG, vector DBs, simple agents), and progressive implementations used for learning and testing different AI concepts.
