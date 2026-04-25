from sentence_transformers import SentenceTransformer
import os

def download():
    model_name = 'all-MiniLM-L6-v2'
    save_path = '/models/all-MiniLM-L6-v2'
    print(f"Downloading {model_name} to {save_path} for offline use...")
    model = SentenceTransformer(model_name)
    model.save(save_path)
    print("Model saved successfully.")

if __name__ == "__main__":
    download()
