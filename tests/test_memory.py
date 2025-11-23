import sys
import os
import uuid
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.reasoning import HybridReasoner

def test_memory():
    print("=" * 80)
    print("TESTING AGENT MEMORY (PostgreSQL)")
    print("=" * 80)

    # Generate unique IDs
    session_id = str(uuid.uuid4())
    user_id = "test_user_" + str(uuid.uuid4())[:8]
    
    print(f"Session ID: {session_id}")
    print(f"User ID: {user_id}")
    
    reasoner = HybridReasoner()
    
    # Interaction 1: Provide personal information
    print("\n1. Telling agent my name...")
    print("-" * 80)
    
    prompt1 = "My name is Dr. House. I am a diagnostician."
    print(f"User: {prompt1}")
    
    response1 = ""
    for chunk in reasoner.triage_stream(prompt1, "N/A", session_id=session_id, user_id=user_id):
        print(chunk, end="", flush=True)
        response1 += chunk
        
    print("\n")
    
    # Interaction 2: Ask for recall
    print("\n2. Asking agent to recall my name...")
    print("-" * 80)
    
    prompt2 = "What is my name and what do I do?"
    print(f"User: {prompt2}")
    
    response2 = ""
    for chunk in reasoner.triage_stream(prompt2, "N/A", session_id=session_id, user_id=user_id):
        print(chunk, end="", flush=True)
        response2 += chunk
        
    print("\n" + "=" * 80)
    
    # Verification
    if "House" in response2 and "diagnostician" in response2.lower():
        print("✅ MEMORY WORKING - Agent recalled name and profession!")
    else:
        print("❌ MEMORY FAILED - Agent did not recall details.")
        
    reasoner.close()

if __name__ == "__main__":
    test_memory()
