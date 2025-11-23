import sys
import os
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agno")
logger.setLevel(logging.INFO)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.reasoning import HybridReasoner

def test_elaborate_output():
    print("=" * 80)
    print("TESTING ELABORATE OUTPUT")
    print("=" * 80)

    session_id = str(uuid.uuid4())
    user_id = "test_patient_elaborate"
    reasoner = HybridReasoner()
    
    # Simple query that could be answered briefly, but we want elaboration
    prompt = "Why does malaria cause fever?"
    
    print(f"\nUser Prompt: {prompt}")
    print("-" * 80)
    
    response_text = ""
    for chunk in reasoner.triage_stream(prompt, "", session_id=session_id, user_id=user_id):
        print(chunk, end="", flush=True)
        response_text += chunk
    print("\n" + "=" * 80)
    
    # Assertions for Elaborateness
    if len(response_text) < 200:
        print(f"\n❌ FAILURE: Response too short ({len(response_text)} chars). Expected elaboration.")
    else:
        print(f"\n✅ SUCCESS: Response is substantial ({len(response_text)} chars).")
        
    reasoner.close()

if __name__ == "__main__":
    test_elaborate_output()
