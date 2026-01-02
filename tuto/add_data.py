import chromadb
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="knowledge_base")

# The data we want to ensure exists
text = "The secret password for the bunker is 'Blueberry'."
id = "secret_doc"

# Generate embedding
response = openai_client.embeddings.create(
    input=text,
    model="text-embedding-3-small"
)
embedding = response.data[0].embedding

# Add it to Chroma
print(f"Adding document: '{text}'")
collection.upsert(
    documents=[text],
    embeddings=[embedding],
    ids=[id]
)
print("Success! Data added.")