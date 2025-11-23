import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.reasoning import HybridReasoner

print("=" * 80)
print("SIMPLE RAG TEST")
print("=" * 80)

reasoner = HybridReasoner()

question = "What is the dosage of metformin for diabetes?"
print(f"\nQuestion: {question}\n")
print("-" * 80)

response = ""
for chunk in reasoner.triage_stream(question, ""):
    print(chunk, end="", flush=True)
    response += chunk

print("\n" + "=" * 80)

if "metformin" in response.lower() and any(dose in response for dose in ["500", "850", "1000", "mg"]):
    print("✅ RAG IS WORKING - Found specific dosage information!")
else:
    print("❌ RAG MIGHT NOT BE WORKING - Response seems generic")

reasoner.close()
