import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.reasoning import HybridReasoner

def test_malaria_response():
    print("Initializing HybridReasoner...")
    reasoner = HybridReasoner()
    
    # Test query matching tutor's feedback scenario
    symptoms = "I have cyclical fever every 48 hours, severe chills, and headache"
    history = "Recently returned from travel to tropical Africa"
    
    print(f"\nTesting with symptoms: {symptoms}")
    print(f"History: {history}")
    print("-" * 70)
    
    # Run the stream
    print("\nAgent Response:\n")
    response_text = ""
    for chunk in reasoner.triage_stream(symptoms, history):
        print(chunk, end="", flush=True)
        response_text += chunk
        
    print("\n" + "-" * 70)
    
    # Check for production-grade qualities
    issues = []
    if "I could not find" in response_text.lower():
        issues.append("❌ EXPOSED RAG FAILURE")
    if "searching" in response_text.lower() or "I will search" in response_text.lower():
        issues.append("❌ META-COMMENTARY DETECTED")
    if "knowledge base" in response_text.lower() or "graph" in response_text.lower():
        issues.append("❌ INTERNAL PROCESS EXPOSED")
    if "malaria" not in response_text.lower():
        issues.append("⚠️ MISSED PRIMARY DIAGNOSIS")
    if "🚨" not in response_text:
        issues.append("⚠️ MISSING STRUCTURED FORMAT")
        
    if issues:
        print("\n\nISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n\n✅ PRODUCTION-GRADE RESPONSE - All checks passed!")

    reasoner.close()

if __name__ == "__main__":
    test_malaria_response()
