import httpx
import asyncio
import sys

async def test_streaming():
    url = "http://localhost:8000/triage"
    payload = {
        "symptoms": "severe headache, sensitivity to light, stiff neck",
        "history": "no prior history"
    }
    
    print(f"Connecting to {url}...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            print("Connected! Streaming response:")
            print("-" * 20)
            async for chunk in response.aiter_text():
                print(chunk, end="", flush=True)
            print("\n" + "-" * 20)

if __name__ == "__main__":
    asyncio.run(test_streaming())
