import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

# 1. Setup
load_dotenv()
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="knowledge_base")

def get_embedding(text):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def ingest_file(filename):
    print(f"Reading {filename}...")
    
    # A. Read the PDF
    reader = PdfReader(filename)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
        
    print(f"Total characters extracted: {len(full_text)}")

    # B. Chunk the text
    # (Simple chunking: every 1000 characters)
    chunk_size = 1000
    chunks = []
    for i in range(0, len(full_text), chunk_size):
        chunks.append(full_text[i:i+chunk_size])
        
    print(f"Created {len(chunks)} chunks.")

    # C. Embed and Store
    print("Embedding and storing in database... (This may take a moment)")
    
    # Prepare lists for Chroma
    ids = []
    embeddings = []
    metadatas = []
    
    for idx, chunk in enumerate(chunks):
        # Create a unique ID for each chunk
        ids.append(f"{filename}_chunk_{idx}")
        
        # Generate vector
        embeddings.append(get_embedding(chunk))
        
        # Store metadata (so we know where this chunk came from later)
        metadatas.append({"source": filename, "chunk_index": idx})

    # Add to Chroma
    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )
    print("Success! PDF ingested.")

if __name__ == "__main__":
    # Make sure you have a file named 'sample.pdf' in your folder!
    # Or change this string to match your file name.
    target_file = "sample.pdf"
    
    if os.path.exists(target_file):
        ingest_file(target_file)
    else:
        print(f"Error: Could not find {target_file}")