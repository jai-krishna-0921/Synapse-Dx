import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.reasoning import HybridReasoner

def test_rag_integration():
    print("Initializing HybridReasoner...")
    reasoner = HybridReasoner()
    
    # Test query that requires both graph and vector search
    symptoms = "severe headache, sensitivity to light, and nausea"
    history = "No prior history of migraines."
    
    print(f"\nTesting with symptoms: {symptoms}")
    print("-" * 50)
    
    # Run the stream
    print("Streaming response...")
    response_text = ""
    for chunk in reasoner.triage_stream(symptoms, history):
        print(chunk, end="", flush=True)
        response_text += chunk
        
    print("\n" + "-" * 50)
    print("\nTest Complete.")
    
    # Check if the response mentions looking up information (heuristic)
    if "migraine" in response_text.lower() or "meningitis" in response_text.lower():
        print("\n✅ SUCCESS: Agent provided relevant medical diagnosis.")
    else:
        print("\n⚠️ WARNING: Agent response might be generic. Check logs for tool usage.")

    reasoner.close()

if __name__ == "__main__":
    test_rag_integration()
