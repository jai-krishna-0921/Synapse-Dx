import json
import time
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

API_URL = "http://localhost:8000/triage"

def test_single_question(item):
    question = item['question']
    # MedQA has options, we just want to see if the diagnosis matches the answer key roughly
    # or just measure latency for now.
    
    payload = {
        "symptoms": question,
        "history": "" 
    }
    
    try:
        start = time.time()
        response = requests.post(API_URL, json=payload)
        end = time.time()
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "latency": data.get("latency_ms", (end-start)*1000),
                "diagnosis": data.get("diagnosis"),
                "answer": item.get("answer")
            }
        else:
            return {"status": "error", "code": response.status_code}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_validation(file_path, limit=10):
    print(f"Loading {file_path}...")
    items = []
    with open(file_path, 'r') as f:
        for line in f:
            items.append(json.loads(line))
            if len(items) >= limit:
                break
    
    print(f"Running validation on {len(items)} items...")
    
    results = []
    latencies = []
    
    with ThreadPoolExecutor(max_workers=1) as executor: # Sequential for accurate latency measurement
        for result in executor.map(test_single_question, items):
            results.append(result)
            if result['status'] == 'success':
                latencies.append(result['latency'])
                print(f"Success: {result['latency']:.2f}ms - Diag: {result['diagnosis']}")
            else:
                print(f"Error: {result}")

    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        print(f"\nAverage Latency: {avg_latency:.2f}ms")
        print(f"Min Latency: {min(latencies):.2f}ms")
        print(f"Max Latency: {max(latencies):.2f}ms")
    else:
        print("No successful requests.")

if __name__ == "__main__":
    run_validation("Validation/medqa_us_test.jsonl", limit=5)
