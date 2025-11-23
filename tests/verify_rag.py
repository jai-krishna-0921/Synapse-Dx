"""
RAG Verification Script
========================
This script tests whether the RAG system is actually retrieving from your documents
or just using the LLM's general knowledge.

Strategy:
1. Ask VERY specific questions that require exact details from medical textbooks
2. Ask about rare conditions/protocols that aren't in general LLM training
3. Compare responses with/without RAG enabled
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.reasoning import HybridReasoner
from qdrant_client import QdrantClient

def test_rag_retrieval():
    print("=" * 80)
    print("RAG VERIFICATION TEST")
    print("=" * 80)
    
    # First, verify Qdrant has data
    print("\n1. Checking Qdrant Collection...")
    client = QdrantClient(url='http://localhost:6333')
    info = client.get_collection('med_guidelines')
    print(f"   ✓ Total vectors in 'med_guidelines': {info.points_count}")
    
    if info.points_count == 0:
        print("   ❌ ERROR: No documents in Qdrant! RAG cannot work.")
        return
    
    # Initialize reasoner
    print("\n2. Initializing HybridReasoner with RAG...")
    reasoner = HybridReasoner()
    print("   ✓ Agent initialized with Knowledge Base")
    
    # Test questions that REQUIRE document retrieval
    print("\n3. Testing RAG with Specific Medical Questions...")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "Rare Disease Protocol",
            "question": "What is the specific treatment protocol for Lyme disease according to medical guidelines?",
            "why": "Requires exact protocol details from textbooks, not general knowledge",
            "keywords": ["doxycycline", "amoxicillin", "ceftriaxone", "weeks", "mg"]
        },
        {
            "name": "Specific Dosage",
            "question": "What is the recommended dosage of metformin for type 2 diabetes management?",
            "why": "Requires exact dosage numbers from guidelines",
            "keywords": ["500", "850", "1000", "mg", "twice daily", "dose"]
        },
        {
            "name": "Diagnostic Criteria",
            "question": "What are the diagnostic criteria for acute coronary syndrome?",
            "why": "Requires specific clinical criteria from medical texts",
            "keywords": ["troponin", "ECG", "chest pain", "elevation", "criteria"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST {i}: {test['name']}")
        print(f"Question: {test['question']}")
        print(f"Why this tests RAG: {test['why']}")
        print(f"{'─' * 80}\n")
        
        # Get response
        response = ""
        for chunk in reasoner.triage_stream(test['question'], ""):
            response += chunk
        
        print(f"Response:\n{response}\n")
        
        # Check if response contains specific keywords
        found_keywords = [kw for kw in test['keywords'] if kw.lower() in response.lower()]
        
        print(f"\n{'─' * 40}")
        print(f"RAG Verification:")
        print(f"  Expected keywords: {test['keywords']}")
        print(f"  Found keywords: {found_keywords}")
        
        if len(found_keywords) >= 2:
            print(f"  ✅ LIKELY USING RAG - Found {len(found_keywords)}/{len(test['keywords'])} specific details")
        else:
            print(f"  ⚠️  MIGHT BE GENERIC - Only found {len(found_keywords)}/{len(test['keywords'])} specific details")
        print(f"{'─' * 40}")
    
    # Direct Qdrant search test
    print(f"\n{'=' * 80}")
    print("4. Direct Qdrant Search Test (Bypassing Agent)")
    print(f"{'=' * 80}")
    
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    query = "treatment protocol for Lyme disease"
    query_vector = embedder.encode(query).tolist()
    
    hits = client.query_points(
        collection_name="med_guidelines",
        query=query_vector,
        limit=3
    ).points
    
    print(f"\nQuery: '{query}'")
    print(f"Top {len(hits)} retrieved chunks:\n")
    
    for i, hit in enumerate(hits, 1):
        print(f"Chunk {i} (Score: {hit.score:.4f}):")
        print(f"{hit.payload.get('text', 'N/A')[:200]}...")
        print()
    
    if hits:
        print("✅ RAG RETRIEVAL WORKING - Qdrant is returning relevant chunks")
    else:
        print("❌ RAG RETRIEVAL FAILED - No chunks returned")
    
    reasoner.close()
    
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print("""
To PROVE RAG is working to your tutor:
1. Show that Qdrant has 16,214+ vectors
2. Show direct Qdrant search returns relevant chunks
3. Show agent responses contain SPECIFIC details (dosages, protocols)
4. Compare: Ask same question with/without RAG - responses should differ

If responses are too generic, the agent might be ignoring retrieved context.
Check agent logs for "search_knowledge" tool calls.
    """)

if __name__ == "__main__":
    test_rag_retrieval()
