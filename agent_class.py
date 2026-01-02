import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from ddgs import DDGS

# Load env variables once at the top
load_dotenv()

class AIAgent:
    def __init__(self):
        """
        Initialize the Agent. 
        This is like the constructor in a React class component.
        We set up the API client and the initial state (memory).
        """
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.messages = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]
        
        # Define the tools schema (configuration)
        self.tools_schema = [
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
                    "description": "Get current weather.",
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
                    "description": "Search the internet for facts.",
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

    # --- Tool Logic (Private Methods) ---
    def _get_current_time(self):
        now = datetime.now()
        return json.dumps({"current_time": now.strftime("%Y-%m-%d %H:%M:%S")})

    def _get_weather(self, location):
        # Mock data for demo
        weather_data = {
            "rabat": "22°C, Sunny",
            "london": "15°C, Rainy",
            "paris": "18°C, Cloudy"
        }
        key = location.lower().split(",")[0].strip()
        result = weather_data.get(key, "Unknown weather data")
        return json.dumps({"location": location, "weather": result})

    def _search_internet(self, query):
        print(f"   🔎 Internal Search: '{query}'...")
        try:
            results = DDGS().text(query, max_results=3)
            if not results: return "No results found."
            summary = ""
            for r in results:
                summary += f"- {r['title']}: {r['body']}\n"
            return summary
        except Exception as e:
            return f"Search error: {e}"

    # --- The Main Logic ---
    def chat(self, user_input):
        """
        This method receives text, handles the thinking,
        runs tools if needed, and returns the final string.
        """
        # 1. Update State
        self.messages.append({"role": "user", "content": user_input})

        # 2. First API Call (Think/Plan)
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            tools=self.tools_schema,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        tool_calls = msg.tool_calls

        if tool_calls:
            self.messages.append(msg) # Save the plan to history
            
            # 3. Execute Tools
            for tool_call in tool_calls:
                fname = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                print(f"   🤖 Agent is using tool: {fname}")
                
                result = "Error"
                if fname == "get_current_time":
                    result = self._get_current_time()
                elif fname == "get_weather":
                    result = self._get_weather(args["location"])
                elif fname == "search_internet":
                    result = self._search_internet(args["query"])
                
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": fname,
                    "content": str(result),
                })

            # 4. Second API Call (Final Answer)
            final_resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages
            )
            ai_reply = final_resp.choices[0].message.content
        else:
            ai_reply = msg.content

        # 5. Final State Update & Return
        self.messages.append({"role": "assistant", "content": ai_reply})
        return ai_reply

# --- Execution Block ---
# This only runs if you run this specific file.
# If you import this file elsewhere, this block is skipped.
if __name__ == "__main__":
    my_agent = AIAgent()
    print("💬 Class-based Agent started! (Type 'exit' to quit)")
    
    while True:
        u_in = input("\nYou: ")
        if u_in.lower() in ["exit", "quit"]:
            break
        
        # Notice how clean the main loop is now:
        response = my_agent.chat(u_in)
        print(f"AI: {response}")