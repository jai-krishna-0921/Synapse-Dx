import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.reasoning import HybridReasoner
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

print("=" * 80)
print("COMPREHENSIVE RAG VERIFICATION")
print("=" * 80)

# Test 1: Direct Qdrant Search
print("\n1. DIRECT QDRANT SEARCH (Bypassing Agent)")
print("-" * 80)

client = QdrantClient(url='http://localhost:6333')
embedder = SentenceTransformer('all-MiniLM-L6-v2')

queries = [
    "metformin dosage for diabetes",
    "Lyme disease treatment protocol",
    "acute coronary syndrome diagnostic criteria"
]

for query in queries:
    print(f"\nQuery: '{query}'")
    query_vector = embedder.encode(query).tolist()
    
    hits = client.query_points(
        collection_name="med_guidelines",
        query=query_vector,
        limit=3
    ).points
    
    if hits:
        print(f"✅ Found {len(hits)} chunks:")
        for i, hit in enumerate(hits, 1):
            text = hit.payload.get('text', 'N/A')
            print(f"\n  Chunk {i} (Score: {hit.score:.4f}):")
            print(f"  {text[:300]}...")
    else:
        print("❌ No chunks found")

# Test 2: Agent with RAG
print("\n\n2. AGENT RESPONSES WITH RAG")
print("=" * 80)

reasoner = HybridReasoner()

test_questions = [
    "What is the recommended dosage of metformin for type 2 diabetes?",
    "What is the treatment protocol for Lyme disease?",
]

for question in test_questions:
    print(f"\nQuestion: {question}")
    print("-" * 80)
    
    response = ""
    for chunk in reasoner.triage_stream(question, ""):
        response += chunk
    
    print(response)
    print("-" * 80)

reasoner.close()

print("\n" * 2)
print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
If you see:
1. ✅ Direct Qdrant search returns relevant chunks
2. ✅ Agent responses contain specific details from those chunks

Then RAG IS WORKING!

If agent refuses to answer despite chunks being available,
the problem is in the agent instructions, not RAG retrieval.
""")
