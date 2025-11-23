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

def test_counter_reasoning():
    print("=" * 80)
    print("TESTING COUNTER-REASONING (Malaria vs Dengue)")
    print("=" * 80)

    session_id = str(uuid.uuid4())
    user_id = "test_patient_logic"
    reasoner = HybridReasoner()
    
    # Turn 1: Initial Symptoms (Suggests Malaria)
    print("\n1. User: 'Returned from Nigeria 10 days ago. Cyclical fever, chills, sweating every 48 hours. Mosquito bites.'")
    print("-" * 80)
    for chunk in reasoner.triage_stream(
        "I recently returned from a 2-week trip to Nigeria about 10 days ago. I have no cough or runny nose, but I am experiencing cycles of extreme shivering chills followed by a high fever and then profuse sweating every 48 hours. I remember getting bitten by mosquitoes during the trip. What could this be?", 
        "", session_id=session_id, user_id=user_id
    ):
        print(chunk, end="", flush=True)
    print("\n")

    # Turn 2: Contradictory Evidence (Suggests Dengue)
    print("\n2. User: 'Actually, the fever is CONSTANT now. And I have a severe RASH and muscle aches.'")
    print("-" * 80)
    
    response_text = ""
    for chunk in reasoner.triage_stream(
        "Actually, I made a mistake. The fever is CONSTANT, not cyclical. And I have a severe RASH all over my body and extreme muscle aches.", 
        "", session_id=session_id, user_id=user_id
    ):
        print(chunk, end="", flush=True)
        response_text += chunk
    print("\n" + "=" * 80)
    
    # Simple assertion check (Case Insensitive)
    if "dengue" in response_text.lower() and "rash" in response_text.lower():
        print("\n✅ SUCCESS: Agent identified Dengue and noted the Rash contradiction.")
    else:
        print("\n❌ FAILURE: Agent failed to switch hypothesis or mention the contradiction.")
    
    reasoner.close()

if __name__ == "__main__":
    test_counter_reasoning()
