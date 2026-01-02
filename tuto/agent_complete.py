import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 1. The Actual "Tool" (Hardcoded for now)
# In a real app, this would hit the OpenWeatherMap API.
def get_weather(location, unit="celsius"):
    """Get the current weather for a specific location."""
    # Mock database of weather
    weather_info = {
        "rabat": "22°C, Sunny",
        "casablanca": "20°C, Partially Cloudy",
        "paris": "12°C, Rainy"
    }
    
    # Normalize input to find key
    key = location.lower().split(",")[0].strip()
    return json.dumps({"location": location, "temperature": weather_info.get(key, "Unknown"), "unit": unit})

# 2. Tool Schema (Same as before)
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The city, e.g. Rabat"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

# 3. First Call: Ask the AI
user_query = "who are you?"
messages = [{"role": "user", "content": user_query}]

print(f"User: {user_query}")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools_schema,
    tool_choice="auto", 
)

response_message = response.choices[0].message
tool_calls = response_message.tool_calls

# 4. Check if AI wants to use a tool
if tool_calls:
    print("🤖 AI wants to use a tool...")
    
    # A. Append the AI's "thought" to the conversation history
    # We must keep the history so the AI remembers what it asked for.
    messages.append(response_message)

    # B. Execute the tool
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        if function_name == "get_weather":
            print(f"⚙️ Executing: get_weather({function_args.get('location')})")
            
            # Run our Python function
            function_response = get_weather(
                location=function_args.get("location"),
                unit=function_args.get("unit")
            )
            
            # C. Send the result back to the AI
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

    # 5. Second Call: Get Final Answer
    # Now the AI has the user question AND the tool output.
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    
    print("\n✅ Final Answer:")
    print(final_response.choices[0].message.content)

else:
    print("AI didn't use any tools.")