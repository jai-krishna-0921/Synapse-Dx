import sys
import os
import uuid

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.reasoning import HybridReasoner

def test_conversational_flow():
    print("=" * 80)
    print("TESTING CONVERSATIONAL AGENT FLOW")
    print("=" * 80)

    session_id = str(uuid.uuid4())
    user_id = "test_patient_" + str(uuid.uuid4())[:8]
    reasoner = HybridReasoner()
    
    # Interaction 1: Vague Symptom (Should trigger questions)
    print("\n1. User: 'I have a fever'")
    print("-" * 80)
    
    response1 = ""
    for chunk in reasoner.triage_stream("I have a fever", "", session_id=session_id, user_id=user_id):
        print(chunk, end="", flush=True)
        response1 += chunk
    print("\n")

    # Interaction 2: General Question (Should answer directly)
    print("\n2. User: 'What are the medications for Type 2 Diabetes?'")
    print("-" * 80)
    
    # New session for general query to avoid context pollution from fever
    session_id_2 = str(uuid.uuid4())
    
    response2 = ""
    for chunk in reasoner.triage_stream("What are the medications for Type 2 Diabetes?", "", session_id=session_id_2, user_id=user_id):
        print(chunk, end="", flush=True)
        response2 += chunk
    print("\n" + "=" * 80)
    
    reasoner.close()

if __name__ == "__main__":
    test_conversational_flow()
