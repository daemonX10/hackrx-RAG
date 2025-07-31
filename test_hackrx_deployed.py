import httpx
import asyncio
import json

# Your deployed Render URL
DEPLOYED_URL = "https://hackrx.onrender.com"

async def test_deployed_hackrx():
    print(f"🧪 Testing HackRx API at: {DEPLOYED_URL}")
    print("⏳ Note: First request may take 30-60 seconds (cold start)")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # 1. Health Check
            print("\n1️⃣ Testing Health Check...")
            health_response = await client.get(f"{DEPLOYED_URL}/health")
            print(f"   Status: {health_response.status_code}")
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"   ✅ Health: {health_data['status']}")
                
                # 2. Test Main Endpoint
                print("\n2️⃣ Testing Main Endpoint...")
                test_payload = {
                    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
                    "questions": ["What is the grace period for premium payment?"]
                }
                
                main_response = await client.post(
                    f"{DEPLOYED_URL}/api/v1/hackrx/run",
                    json=test_payload
                )
                print(f"   Status: {main_response.status_code}")
                
                if main_response.status_code == 200:
                    result = main_response.json()
                    print(f"   ✅ Answer: {result['answers'][0][:100]}...")
                    
                    print("\n🎉 SUCCESS! Your HackRx API is ready!")
                    print(f"📝 Submit this URL to HackRx: {DEPLOYED_URL}/api/v1/hackrx/run")
                    print(f"📊 API Documentation: {DEPLOYED_URL}/docs")
                else:
                    print(f"   ❌ Error: {main_response.text}")
            else:
                print(f"   ❌ Health check failed: {health_response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 If this is the first request, the service might still be starting up.")

if __name__ == "__main__":
    asyncio.run(test_deployed_hackrx())
