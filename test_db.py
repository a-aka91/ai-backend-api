import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

# Try to insert a row
data, count = supabase.table('messages').insert({
    "role": "system", 
    "content": "Database Connection Successful! 🚀"
}).execute()

print("Inserted:", data)