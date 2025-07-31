import httpx
import asyncio
import json

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_DOCUMENT_URL = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"

async def test_health_check():
    """Test health check endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Health Check Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200

async def test_main_endpoint():
    """Test the main hackrx/run endpoint"""
    test_payload = {
        "documents": TEST_DOCUMENT_URL,
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?"
        ]
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/hackrx/run",
            json=test_payload
        )
        
        print(f"Main Endpoint Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Number of answers: {len(result['answers'])}")
            for i, answer in enumerate(result['answers']):
                print(f"Q{i+1}: {answer[:100]}...")
        else:
            print(f"Error: {response.text}")
        
        return response.status_code == 200

async def test_detailed_endpoint():
    """Test the detailed endpoint"""
    test_payload = {
        "documents": TEST_DOCUMENT_URL,
        "questions": [
            "What is the No Claim Discount (NCD) offered in this policy?"
        ]
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/hackrx/run/detailed",
            json=test_payload
        )
        
        print(f"Detailed Endpoint Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Processing time: {result.get('processing_time', 'N/A')}s")
            print(f"Total tokens used: {result.get('total_tokens_used', 'N/A')}")
            
            if result.get('detailed_responses'):
                detail = result['detailed_responses'][0]
                print(f"Confidence: {detail['confidence_score']}")
                print(f"Reasoning: {detail['reasoning'][:100]}...")
        else:
            print(f"Error: {response.text}")
        
        return response.status_code == 200

async def test_document_analysis():
    """Test document analysis endpoint"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/analyze-document",
            params={"document_url": TEST_DOCUMENT_URL}
        )
        
        print(f"Document Analysis Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Document type: {result.get('document_type')}")
            print(f"Total chunks: {result.get('total_chunks')}")
            print(f"Total words: {result.get('total_words')}")
        else:
            print(f"Error: {response.text}")
        
        return response.status_code == 200

async def run_all_tests():
    """Run all tests"""
    print("🧪 Starting API Tests...\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("Main Endpoint", test_main_endpoint),
        ("Detailed Endpoint", test_detailed_endpoint),
        ("Document Analysis", test_document_analysis)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🔍 Running {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}\n")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ FAILED - Error: {e}\n")
    
    # Summary
    print("📊 Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    print("🚀 HackRx 6.0 API Testing Suite")
    print(f"Testing API at: {BASE_URL}")
    print("Make sure the server is running before running tests!\n")
    
    success = asyncio.run(run_all_tests())
    
    if success:
        print("🎉 All tests passed! Your API is ready for submission.")
    else:
        print("⚠️  Some tests failed. Please check your implementation.")
