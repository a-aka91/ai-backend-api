import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

# 1. Setup
load_dotenv()
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Initialize ChromaDB in "Persistent" mode
# This creates a folder named "chroma_db" in your project to store data
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create (or get) a collection. Think of this like a "Table" in SQL.
collection = chroma_client.get_or_create_collection(name="knowledge_base")

# Helper function from yesterday
def get_embedding(text):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

# 2. Add Data to the Database
# We only want to add data if the collection is empty (to avoid duplicates for this test)
if collection.count() == 0:
    print("Database is empty. Adding documents...")
    
    docs = [
        "The python programming language is great for AI.",
        "Apples and bananas are rich in potassium.",
        "To restart the server, run sudo systemctl restart nginx.",
        "My name is Anas, I'm 35 years old.",
        "React uses a virtual DOM to optimize rendering."
    ]
    
    # We must generate embeddings for each doc before storing
    # (In production, you do this in batches, but a loop is fine for now)
    embeddings = [get_embedding(d) for d in docs]
    ids = ["doc1", "doc2", "doc3", "doc4", "doc5"]
    
    collection.add(
        documents=docs,
        embeddings=embeddings,
        ids=ids
    )
    print("Documents added!")
else:
    print("Documents already exist in the database.")

# 3. Search the Database
query_text = "What's my name?"
print(f"\nQuerying: '{query_text}'")

# Convert query to vector
query_vector = get_embedding(query_text)

# Ask Chroma to find the top 1 match
results = collection.query(
    query_embeddings=[query_vector],
    n_results=1
)

# 4. Display Results
print("\n--- Result ---")
print(f"Document: {results['documents'][0][0]}")
print(f"ID: {results['ids'][0][0]}")
# Chroma returns 'distance' (lower is better), unlike cosine similarity (higher is better)
print(f"Distance Score: {results['distances'][0][0]:.4f}")