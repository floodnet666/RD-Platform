from sentence_transformers import SentenceTransformer
import os

def download():
    model_name = 'all-MiniLM-L6-v2'
    print(f"Downloading {model_name} for offline use...")
    model = SentenceTransformer(model_name)
    print("Model downloaded successfully.")

if __name__ == "__main__":
    download()
