import os
import math
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 1. Our "Database" of knowledge
# In a real app, this would be your PDF chunks stored in a database.
documents = [
    "The python programming language is great for AI.",
    "Apples and bananas are rich in potassium.",
    "To restart the server, run sudo systemctl restart nginx.",
    "React uses a virtual DOM to optimize rendering.",
]

def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def cosine_similarity(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude_v1 = math.sqrt(sum(a * a for a in v1))
    magnitude_v2 = math.sqrt(sum(b * b for b in v2))
    return dot_product / (magnitude_v1 * magnitude_v2)

def search_database(query):
    print(f"Analyzing query: '{query}'...")
    
    # A. Convert query to vector
    query_vec = get_embedding(query)
    
    results = []
    
    # B. Loop through every document (The "Retrieval" part)
    for doc in documents:
        doc_vec = get_embedding(doc)
        score = cosine_similarity(query_vec, doc_vec)
        results.append({
            "content": doc,
            "score": score
        })
    
    # C. Sort by highest score
    # (Lambda explanation: Sort the list based on the 'score' key)
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[0]

if __name__ == "__main__":
    # Test 1: Ask about fruit
    best_match = search_database("What is a healthy snack?")
    print(f"\nWINNER: {best_match['content']} (Score: {best_match['score']:.4f})")

    print("-" * 30)

    # Test 2: Ask about code
    best_match = search_database("How do I fix the web server?")
    print(f"\nWINNER: {best_match['content']} (Score: {best_match['score']:.4f})")