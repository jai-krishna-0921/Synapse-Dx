import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.reasoning import HybridReasoner

print("=" * 80)
print("TESTING RAG WITH DEBUG MODE")
print("=" * 80)

reasoner = HybridReasoner()

print("\nAsking: 'What is the dosage of metformin?'")
print("-" * 80)

response = ""
for chunk in reasoner.triage_stream('What is the dosage of metformin?', ''):
    print(chunk, end='', flush=True)
    response += chunk

print("\n" + "=" * 80)
print("Check above for DEBUG logs showing knowledge search calls")
print("=" * 80)

reasoner.close()
