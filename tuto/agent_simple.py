import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 1. Define the Tool (The "Menu" for the AI)
# We describe what functions are available in a specific JSON format.
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

# 2. The User Query
# We ask a question that requires external data.
user_query = "What is the weather like in Rabat, Morocco today?"

print(f"User: {user_query}")

# 3. Send to OpenAI with Tools
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": user_query}],
    tools=tools_schema, # <--- We pass the tools here
    tool_choice="auto", # <--- We let the AI decide if it needs a tool
)

# 4. Inspect the Result
# The model should NOT return content. It should return a tool_call.
message = response.choices[0].message

if message.tool_calls:
    print("\n✅ AI decided to use a tool!")
    tool_call = message.tool_calls[0]
    print(f"Tool Name: {tool_call.function.name}")
    print(f"Arguments: {tool_call.function.arguments}")
else:
    print("\n❌ AI just chatted normally.")
    print(message.content)