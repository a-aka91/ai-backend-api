import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
from agent_class import AIAgent

load_dotenv()

# --- 1. SETUP DATABASE ---
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

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

# --- 2. HELPER FUNCTIONS ---
def save_message(role: str, content: str):
    """Saves a message to Supabase"""
    try:
        supabase.table("messages").insert({"role": role, "content": content}).execute()
    except Exception as e:
        print(f"Error saving to DB: {e}")

def get_recent_history(limit=5):
    """Fetches the last N messages to give the AI context"""
    try:
        # Get last N messages (ordered by newest first)
        response = supabase.table("messages").select("*").order("id", desc=True).limit(limit).execute()
        # Reverse them so they are in chronological order (Oldest -> Newest)
        history = response.data[::-1]
        
        # Format for OpenAI (needs 'role' and 'content')
        formatted_history = [{"role": msg["role"], "content": msg["content"]} for msg in history]
        return formatted_history
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

# --- 3. THE SMART GENERATOR ---
def response_generator(user_prompt: str):
    
    # A. Save User Message to DB
    save_message("user", user_prompt)

    # B. Fetch History (So it remembers previous chats)
    history = get_recent_history()
    
    # C. Add System Prompt
    system_instruction = {"role": "system", "content": "You are a helpful assistant. You must answer in Arabic (or Darija) so the text-to-speech engine can read your response correctly."}
    messages = [system_instruction] + history 

    # D. Call OpenAI²
    stream = agent.client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )

    # E. Stream & Accumulate
    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            text_chunk = chunk.choices[0].delta.content
            full_response += text_chunk
            yield text_chunk

    # F. Save AI Response to DB (After stream finishes)
    save_message("assistant", full_response)


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    return StreamingResponse(response_generator(request.prompt), media_type="text/plain")

@app.get("/")
def read_root():
    return {"status": "AI Memory Online"}