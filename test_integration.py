#!/usr/bin/env python3
"""
Automated test script for Claims Triage Agent
Tests the full integration between frontend and backend
"""

import requests
import time
import json
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def test_api_health():
    """Test API health endpoint."""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy: {data['service']} v{data['version']}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

def test_file_upload():
    """Test file upload functionality."""
    print("\n📤 Testing file upload...")
    try:
        # Use the test PDF we created
        pdf_path = Path("test_claim.pdf")
        if not pdf_path.exists():
            print("❌ Test PDF not found")
            return False
        
        with open(pdf_path, 'rb') as f:
            files = {'file': ('test_claim.pdf', f, 'application/pdf')}
            response = requests.post(f"{API_BASE_URL}/upload/claim", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ File uploaded successfully: {data['claim_id']}")
            return data['claim_id']
        else:
            print(f"❌ File upload failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ File upload error: {e}")
        return None

def test_claims_retrieval():
    """Test claims retrieval."""
    print("\n📋 Testing claims retrieval...")
    try:
        response = requests.get(f"{API_BASE_URL}/claims")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {data['total']} claims")
            if data['claims']:
                claim = data['claims'][0]
                print(f"   📄 Sample claim: {claim['id']}")
                print(f"   🎯 Severity: {claim['severity']}/10")
                print(f"   📊 Complexity: {claim['complexity']}")
                print(f"   👥 Team: {claim['suggested_team']}")
                print(f"   🚩 Flags: {', '.join(claim['flags'])}")
            return True
        else:
            print(f"❌ Claims retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Claims retrieval error: {e}")
        return False

def test_claim_reassignment(claim_id):
    """Test claim reassignment."""
    print(f"\n🔄 Testing claim reassignment for {claim_id}...")
    try:
        new_team = "Test Team Assignment"
        response = requests.post(
            f"{API_BASE_URL}/claims/{claim_id}/reassign",
            json={"new_team": new_team}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Claim reassigned successfully to: {data['new_team']}")
            return True
        else:
            print(f"❌ Claim reassignment failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Claim reassignment error: {e}")
        return False

def test_frontend_accessibility():
    """Test if frontend is accessible."""
    print("\n🌐 Testing frontend accessibility...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend accessibility error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Claims Triage Agent Integration Tests")
    print("=" * 50)
    
    # Test results
    results = {
        "api_health": False,
        "file_upload": False,
        "claims_retrieval": False,
        "claim_reassignment": False,
        "frontend_accessibility": False
    }
    
    # Run tests
    results["api_health"] = test_api_health()
    
    if results["api_health"]:
        claim_id = test_file_upload()
        results["file_upload"] = claim_id is not None
        
        if claim_id:
            # Wait for background processing
            print("\n⏳ Waiting for background processing...")
            time.sleep(5)
            
            results["claims_retrieval"] = test_claims_retrieval()
            results["claim_reassignment"] = test_claim_reassignment(claim_id)
    
    results["frontend_accessibility"] = test_frontend_accessibility()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Integration is working correctly.")
        print(f"\n🌐 Frontend: {FRONTEND_URL}")
        print(f"🔧 API Docs: {API_BASE_URL}/docs")
    else:
        print("⚠️  Some tests failed. Check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
