import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from ddgs import DDGS

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 1. The Real Search Tool
def search_internet(query):
    """Searches the internet for the given query."""
    print(f"🔎 Searching the web for: '{query}'...")
    results = DDGS().text(query, max_results=3)
    
    if not results:
        return "No results found."
        
    # Combine the top 3 snippets into one string
    summary = ""
    for result in results:
        summary += f"- {result['title']}: {result['body']}\n"
    
    return summary

# 2. Tool Schema
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "search_internet",
            "description": "Search the internet for current events, facts, or news.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to send to the search engine.",
                    },
                },
                "required": ["query"],
            },
        },
    }
]

# 3. Ask a Question that requires Live Data
# GPT-4o-mini's training data cuts off in late 2023/early 2024.
# Asking about something very recent proves it's using the tool.
user_query = "Who won the latest Super Bowl and what was the score?"
# OR try: "What is the current price of Bitcoin?"

messages = [{"role": "user", "content": user_query}]
print(f"User: {user_query}")

# 4. First Call: Planning
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools_schema,
    tool_choice="auto", 
)

response_message = response.choices[0].message
tool_calls = response_message.tool_calls

if tool_calls:
    messages.append(response_message) # Add the "plan" to history

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        if function_name == "search_internet":
            # A. Execute the search
            search_query = function_args.get("query")
            tool_output = search_internet(search_query)
            
            # B. Send results back to AI
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": tool_output,
            })

    # 5. Second Call: Final Answer
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    
    print("\n✅ AI Answer:")
    print(final_response.choices[0].message.content)

else:
    print("AI decided not to search.")
    print(response_message.content)