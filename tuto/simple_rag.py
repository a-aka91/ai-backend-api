import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

# 1. Setup
load_dotenv()
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="knowledge_base")

def get_embedding(text):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def query_database(query_text):
    # 2. Retrieval (The "R" in RAG)
    results = collection.query(
        query_embeddings=[get_embedding(query_text)],
        n_results=1
    )
    
    # Check if we actually found something
    if not results['documents'][0]:
        return None
        
    return results['documents'][0][0]

def generate_answer(query, context):
    # 3. Augmented Generation (The "AG" in RAG)
    
    # We construct a specific prompt that forces the AI to look at our data
    prompt = f"""
    You are a helpful assistant. Use the provided context to answer the question.
    If the answer is not in the context, say "I don't know."
    
    Context: {context}
    
    Question: {query}
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# 4. The Main Loop
if __name__ == "__main__":
    print("--- RAG AI Assistant ---")
    user_query = input("Ask a question: ")
    
    print("Searching database...")
    retrieved_context = query_database(user_query)
    
    if retrieved_context:
        print(f"Found context: {retrieved_context}")
        print("Generating answer...")
        final_answer = generate_answer(user_query, retrieved_context)
        print(f"\nAI Answer: {final_answer}")
    else:
        print("No relevant info found in database.")