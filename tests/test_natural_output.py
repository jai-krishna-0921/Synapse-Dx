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

def test_natural_output():
    print("=" * 80)
    print("TESTING NATURAL OUTPUT (Meningitis Scenario)")
    print("=" * 80)

    session_id = str(uuid.uuid4())
    user_id = "test_patient_natural"
    reasoner = HybridReasoner()
    
    # User provides detailed symptoms
    prompt = """
    I’m contacting you because I thought I just had a bad case of the flu, but now I’m not so sure. I’ve had a high fever and body aches since yesterday, which seemed normal enough.
    But this morning, I woke up with the worst headache of my life—it feels like my head is in a vice. I tried to check my phone, but looking down is agonizing; my neck feels incredibly stiff and rigid, like I can’t even touch my chin to my chest.
    I’ve also been keeping the curtains drawn all day because the sunlight hurts my eyes way too much. I just threw up a few minutes ago. Should I just keep resting, or is this something else?
    """
    
    print(f"\nUser Prompt: {prompt.strip()[:100]}...")
    print("-" * 80)
    
    response_text = ""
    for chunk in reasoner.triage_stream(prompt, "", session_id=session_id, user_id=user_id):
        print(chunk, end="", flush=True)
        response_text += chunk
    print("\n" + "=" * 80)
    
    # Assertions for Natural Style
    if "Primary Hypothesis:" in response_text or "🚨" in response_text:
        print("\n❌ FAILURE: Output still contains robotic headers/icons.")
    elif "since you mentioned" in response_text.lower() or "given your symptoms" in response_text.lower() or "because" in response_text.lower():
        print("\n✅ SUCCESS: Agent used natural reasoning phrasing.")
    else:
        print("\n⚠️ WARNING: Output might be natural but didn't use expected phrases. Check manually.")
    
    reasoner.close()

if __name__ == "__main__":
    test_natural_output()
