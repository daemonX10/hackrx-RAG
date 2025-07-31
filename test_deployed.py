import httpx
import asyncio
import sys

# Update this URL after deployment
DEPLOYED_URL = "https://your-app-name.onrender.com"

async def test_deployed_api():
    """Test the deployed API"""
    print(f"🧪 Testing deployed API at: {DEPLOYED_URL}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Test health endpoint
            print("1. Testing health endpoint...")
            health_response = await client.get(f"{DEPLOYED_URL}/health")
            print(f"   Status: {health_response.status_code}")
            
            if health_response.status_code == 200:
                print("   ✅ Health check passed")
                
                # Test main endpoint
                print("2. Testing main endpoint...")
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
                    print(f"   ✅ Main endpoint working - Answer: {result['answers'][0][:100]}...")
                    print(f"\n🎉 API is ready for HackRx submission!")
                    print(f"📝 Submission URL: {DEPLOYED_URL}/api/v1/hackrx/run")
                else:
                    print(f"   ❌ Main endpoint failed: {main_response.text}")
            else:
                print(f"   ❌ Health check failed: {health_response.text}")
                
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        print("💡 Make sure the deployed service is running and URL is correct")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        DEPLOYED_URL = sys.argv[1].rstrip('/')
    
    print("Usage: python test_deployed.py [URL]")
    print(f"Example: python test_deployed.py https://hackrx-solution.onrender.com")
    print()
    
    asyncio.run(test_deployed_api())
