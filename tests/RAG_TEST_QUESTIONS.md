# RAG Verification Questions
# ===========================
# These questions can ONLY be answered correctly if RAG is retrieving from your medical documents.
# General LLMs will give vague or incorrect answers.

## Category 1: Specific Dosages (Requires Exact Numbers)
1. "What is the recommended starting dose of metformin for type 2 diabetes?"
   - RAG should return: "500mg or 850mg twice daily" (from guidelines)
   - Generic LLM: Vague answer without specific mg

2. "What is the dosage of doxycycline for Lyme disease treatment?"
   - RAG should return: "100mg twice daily for 10-21 days"
   - Generic LLM: May not know exact duration

## Category 2: Rare Conditions (Not in General Training)
3. "What are the diagnostic criteria for Kawasaki disease?"
   - RAG should return: Specific fever duration + clinical criteria
   - Generic LLM: May confuse with other pediatric conditions

4. "What is the treatment for Whipple's disease?"
   - RAG should return: Specific antibiotic regimen (e.g., TMP-SMX)
   - Generic LLM: Unlikely to know this rare condition

## Category 3: Specific Protocols (Requires Guidelines)
5. "What is the CURB-65 score for pneumonia severity assessment?"
   - RAG should return: Exact criteria (Confusion, Urea, Respiratory rate, BP, age ≥65)
   - Generic LLM: May know acronym but not exact thresholds

6. "What are the Rome IV criteria for irritable bowel syndrome?"
   - RAG should return: Specific symptom frequency and duration
   - Generic LLM: May give outdated Rome III criteria

## Category 4: Drug Interactions (Requires Pharmacology Texts)
7. "What drugs should be avoided with warfarin?"
   - RAG should return: Specific list from pharmacology texts
   - Generic LLM: May give incomplete list

8. "What is the mechanism of action of methotrexate in rheumatoid arthritis?"
   - RAG should return: Detailed mechanism from textbooks
   - Generic LLM: May give simplified explanation

## Category 5: Differential Diagnosis Trees (Requires Clinical Algorithms)
9. "What is the differential diagnosis for acute abdominal pain in the right lower quadrant?"
   - RAG should return: Structured list from clinical algorithms
   - Generic LLM: May miss rare causes

10. "What are the causes of elevated troponin besides myocardial infarction?"
    - RAG should return: Comprehensive list from cardiology texts
    - Generic LLM: May only mention MI

## How to Test:
1. Run: `venv/bin/python tests/verify_rag.py`
2. Or ask these questions directly in the frontend at http://localhost:3000
3. Check if responses contain SPECIFIC details (numbers, exact criteria, drug names)
4. If responses are vague, RAG might not be working

## Expected RAG Indicators:
✅ Exact dosages (e.g., "500mg twice daily")
✅ Specific durations (e.g., "10-21 days")
✅ Clinical criteria with numbers (e.g., "fever >5 days")
✅ Drug names with mechanisms
✅ Structured protocols from guidelines

## Red Flags (Generic LLM):
❌ Vague answers ("appropriate dose")
❌ Missing numbers
❌ "Consult a doctor" without specifics
❌ Outdated information
