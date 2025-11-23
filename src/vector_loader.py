import os
import glob
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from dotenv import load_dotenv
import uuid

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "med_guidelines"

class VectorLoader:
    def __init__(self):
        # Increase timeout significantly for large files
        self.client = QdrantClient(url=QDRANT_URL, timeout=300.0)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_size = 384 # Dimension of all-MiniLM-L6-v2

    def create_collection(self):
        print(f"Creating collection {COLLECTION_NAME}...")
        if not self.client.collection_exists(collection_name=COLLECTION_NAME):
             self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )
             print("Collection created.")
        else:
             print(f"Collection {COLLECTION_NAME} already exists.")

    def read_text_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def read_pdf_file(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    def chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        # Simple word-based chunking for now
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i:i + chunk_size]))
        return chunks

    def process_files(self, file_paths: List[str]):
        points = []
        total_chunks = 0
        
        for file_path in file_paths:
            print(f"Processing {file_path}...")
            try:
                if file_path.endswith('.pdf'):
                    text = self.read_pdf_file(file_path)
                else:
                    text = self.read_text_file(file_path)
                
                chunks = self.chunk_text(text)
                
                for i, chunk in enumerate(chunks):
                    if not chunk.strip():
                        continue
                        
                    embedding = self.model.encode(chunk).tolist()
                    point_id = str(uuid.uuid4())
                    
                    points.append(PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "name": f"{os.path.basename(file_path)}_chunk_{i}",  # Required by Agno
                            "meta_data": {}, # Required by Agno
                            "content": chunk, # Required by Agno
                            "source": os.path.basename(file_path),
                            "text": chunk,
                            "chunk_index": i
                        }
                    ))
                    total_chunks += 1
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

            # Upload in smaller batches to avoid timeouts
            if len(points) >= 10:
                self.upsert_batch(points)
                points = []
                print(f"Uploaded batch. Total chunks: {total_chunks}")
                # Small delay to let Qdrant catch up
                import time
                time.sleep(0.1)

        # Upload remaining
        if points:
            self.upsert_batch(points)
            print(f"Uploaded final batch. Total chunks: {total_chunks}")

    def upsert_batch(self, points):
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points
                )
                return
            except Exception as e:
                print(f"Upsert failed (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1)) # Exponential backoff
                else:
                    print("Skipping batch after max retries.")

def main():
    loader = VectorLoader()
    
    # Find files
    text_files = glob.glob("Docs/textbooks/*.txt")
    pdf_files = glob.glob("Docs/*.pdf")
    all_files = text_files + pdf_files
    
    # Robust exclusion
    filtered_files = []
    for f in all_files:
        if "InternalMed_Harrison.txt" in os.path.basename(f) or "Surgery_Schwartz.txt" in os.path.basename(f):
            print(f"Skipping {f} (too large/problematic)")
            continue
        filtered_files.append(f)
    
    print(f"Found {len(filtered_files)} files to process (excluded Harrison & Schwartz).")
    
    # Force recreate to avoid duplicates from partial runs
    print(f"Recreating collection {COLLECTION_NAME}...")
    if loader.client.collection_exists(collection_name=COLLECTION_NAME):
        loader.client.delete_collection(collection_name=COLLECTION_NAME)
    
    loader.client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=loader.vector_size, distance=Distance.COSINE),
    )
    
    loader.process_files(filtered_files)

if __name__ == "__main__":
    main()
