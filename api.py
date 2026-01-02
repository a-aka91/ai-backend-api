from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse # <--- NEW IMPORT
from pydantic import BaseModel
from agent_class import AIAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = AIAgent()

class ChatRequest(BaseModel):
    prompt: str

# --- THE NEW STREAMING LOGIC ---
def response_generator(prompt: str):
    """
    This function talks to OpenAI with stream=True
    and 'yields' chunks of text as they arrive.
    """
    # We are bypassing the agent.run() method slightly here for the demo
    # to access the raw stream from the client inside your agent
    stream = agent.client.chat.completions.create(
        model="gpt-4o-mini", # Or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": agent.messages[0]["content"]}, # Keep the system prompt
            {"role": "user", "content": prompt}
        ],
        stream=True, # <--- CRITICAL: asking OpenAI to stream
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    # Instead of returning JSON, we return a StreamingResponse
    # We pass the generator function to it
    return StreamingResponse(response_generator(request.prompt), media_type="text/plain")