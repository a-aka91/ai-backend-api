import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from ddgs import DDGS

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- 1. Define the Python Functions ---

def get_current_time():
    """Returns the current date and time."""
    now = datetime.now()
    return json.dumps({"current_time": now.strftime("%Y-%m-%d %H:%M:%S")})

def get_weather(location):
    """Mock weather function."""
    # In a real app, you'd fetch from an API. We'll mock it for speed.
    weather_data = {
        "rabat": "22°C, Sunny",
        "london": "15°C, Rainy",
        "new york": "10°C, Cloudy"
    }
    key = location.lower().split(",")[0].strip()
    result = weather_data.get(key, "Unknown weather data")
    return json.dumps({"location": location, "weather": result})

def search_internet(query):
    """Searches the web using DuckDuckGo."""
    print(f"🔎 Searching for: '{query}'...")
    results = DDGS().text(query, max_results=3)
    if not results:
        return "No results found."
    summary = ""
    for r in results:
        summary += f"- {r['title']}: {r['body']}\n"
    return summary

# --- 2. Define the Tool Schemas (The Menu) ---

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time.",
            # No parameters needed for time
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

# --- 3. The Agent Logic ---

def run_agent(user_query):
    print(f"\nUser: {user_query}")
    messages = [{"role": "user", "content": user_query}]

    # A. First Call: Planning
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools_schema,
        tool_choice="auto",
    )
    
    msg = response.choices[0].message
    tool_calls = msg.tool_calls

    if tool_calls:
        messages.append(msg) # Add AI's plan to history
        
        # B. Execution Loop
        for tool_call in tool_calls:
            fname = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"🤖 AI chose tool: {fname}")

            # Route to the correct function
            if fname == "get_current_time":
                result = get_current_time()
            elif fname == "get_weather":
                result = get_weather(args["location"])
            elif fname == "search_internet":
                result = search_internet(args["query"])
            else:
                result = "Error: Tool not found"
            
            # C. Send Result back to AI
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": fname,
                "content": str(result),
            })

        # D. Second Call: Final Answer
        final_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        print(f"✅ AI: {final_resp.choices[0].message.content}")
    
    else:
        # No tools needed
        print(f"✅ AI: {msg.content}")

# --- 4. Test it! ---

if __name__ == "__main__":
    # Test 1: Needs Weather Tool
    # run_agent("Is it raining in London right now?")
    
    # Test 2: Needs Search Tool
    # run_agent("Who is the CEO of OpenAI?")

    # Test 3: Needs Time Tool
    # run_agent("What is today's date?")

    # Test 4: The Combo Move
    run_agent("What is the weather in Rabat, and who is the current CEO of OpenAI?")