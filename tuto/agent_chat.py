import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from ddgs import DDGS

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- 1. Define Tools (Same as yesterday) ---

def get_current_time():
    now = datetime.now()
    return json.dumps({"current_time": now.strftime("%Y-%m-%d %H:%M:%S")})

def get_weather(location):
    weather_data = {
        "rabat": "22°C, Sunny",
        "london": "15°C, Rainy",
        "new york": "10°C, Cloudy"
    }
    key = location.lower().split(",")[0].strip()
    result = weather_data.get(key, "Unknown weather data")
    return json.dumps({"location": location, "weather": result})

def search_internet(query):
    print(f"🔎 Searching for: '{query}'...")
    results = DDGS().text(query, max_results=3)
    if not results:
        return "No results found."
    summary = ""
    for r in results:
        summary += f"- {r['title']}: {r['body']}\n"
    return summary

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time.",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_internet",
            "description": "Search the internet for current events or facts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                },
                "required": ["query"],
            },
        },
    }
]

# --- 2. Initialize "State" (Global Memory) ---
# In React, this is: const [messages, setMessages] = useState([...])
messages = [
    {"role": "system", "content": "You are a helpful AI assistant with access to tools."}
]

# --- 3. The Chat Loop (The Event Listener) ---
print("💬 Chat started! Type 'exit' to stop.")

while True:
    # A. Get User Input
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    # B. Add user message to state
    messages.append({"role": "user", "content": user_input})

    # C. First Call: Think & Plan
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools_schema,
        tool_choice="auto",
    )
    
    msg = response.choices[0].message
    tool_calls = msg.tool_calls

    if tool_calls:
        messages.append(msg) # Remember the plan
        
        # D. Execute Tools
        for tool_call in tool_calls:
            fname = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"🤖 Tool used: {fname}")

            if fname == "get_current_time":
                result = get_current_time()
            elif fname == "get_weather":
                result = get_weather(args["location"])
            elif fname == "search_internet":
                result = search_internet(args["query"])
            else:
                result = "Error: Tool not found"
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": fname,
                "content": str(result),
            })

        # E. Second Call: Final Answer
        final_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        ai_reply = final_resp.choices[0].message.content
        print(f"AI: {ai_reply}")
        
        # F. Update State
        messages.append({"role": "assistant", "content": ai_reply})

    else:
        # No tools used, just normal chat
        ai_reply = msg.content
        print(f"AI: {ai_reply}")
        messages.append({"role": "assistant", "content": ai_reply})