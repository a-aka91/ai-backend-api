import os
import math
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    # The API returns a list of objects, we want the embedding vector from the first one
    return response.data[0].embedding

# if __name__ == "__main__":
#     word = "Apple"
#     vector = get_embedding(word)
    
#     print(f"Word: {word}")
#     print(f"Vector length: {len(vector)}")
#     print(f"First 5 dimensions: {vector[:5]}")

# import math

# A manual function to calculate Cosine Similarity
# (1.0 = Identical, 0.0 = Totally different, -1.0 = Opposite)
def cosine_similarity(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude_v1 = math.sqrt(sum(a * a for a in v1))
    magnitude_v2 = math.sqrt(sum(b * b for b in v2))
    return dot_product / (magnitude_v1 * magnitude_v2)

if __name__ == "__main__":
    # 1. Get vectors for 3 words
    vec_apple = get_embedding("Man")
    vec_banana = get_embedding("Woman")
    vec_truck = get_embedding("Boy")

    # 2. Compare them
    similarity_a_b = cosine_similarity(vec_apple, vec_banana)
    similarity_a_t = cosine_similarity(vec_apple, vec_truck)

    print(f"Similarity (King <-> Queen): {similarity_a_b:.4f}")
    print(f"Similarity (King <-> Man):  {similarity_a_t:.4f}")