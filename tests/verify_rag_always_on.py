import sys
import os
import uuid
import logging

# Configure logging to show Agno's debug output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agno")
logger.setLevel(logging.INFO)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.reasoning import HybridReasoner

def verify_rag_always_on():
    print("=" * 80)
    print("TESTING RAG FOR GENERAL QUESTIONS")
    print("=" * 80)

    session_id = str(uuid.uuid4())
    user_id = "test_user"
    reasoner = HybridReasoner()
    
    # General Question
    query = "What is the dosage of Amoxicillin for otitis media?"
    print(f"\nQuery: '{query}'")
    print("-" * 80)
    
    # We want to see if it retrieves documents. 
    # Since we can't easily capture internal logs of the Agent class from here without mocking,
    # we will rely on the output containing specific details that would likely come from the docs,
    # AND we will look at the stdout which should show "Found X documents" if logging is enabled in the app.
    
    response = ""
    for chunk in reasoner.triage_stream(query, "", session_id=session_id, user_id=user_id):
        print(chunk, end="", flush=True)
        response += chunk
    print("\n" + "=" * 80)
    
    reasoner.close()

if __name__ == "__main__":
    verify_rag_always_on()
