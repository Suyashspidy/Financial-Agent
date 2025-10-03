#!/usr/bin/env python3
"""
Financial Agent Complete Integration Test
Tests the full integration between all components
"""

import requests
import time
import json
from pathlib import Path

def test_service_health():
    """Test all service health endpoints"""
    print("🔍 Testing service health...")
    
    services = [
        ("Frontend", "http://localhost:5173"),
        ("Enhanced Claims API", "http://localhost:8000/health"),
        ("LandingAI MCP Server", "http://localhost:8001/health"),
        ("Inkeep UI", "http://localhost:3000"),
        ("Manage UI", "http://localhost:2001"),
        ("Inkeep Manage API", "http://localhost:3002"),
        ("Inkeep Run API", "http://localhost:3003")
    ]
    
    all_healthy = True
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {service_name}: Healthy")
            else:
                print(f"   ❌ {service_name}: Unhealthy (Status: {response.status_code})")
                all_healthy = False
        except Exception as e:
            print(f"   ❌ {service_name}: Not accessible ({str(e)})")
            all_healthy = False
    
    return all_healthy

def test_document_upload():
    """Test document upload functionality"""
    print("\n📤 Testing document upload...")
    
    # Create a test PDF file if it doesn't exist
    test_pdf_path = Path("test_claim.pdf")
    if not test_pdf_path.exists():
        print("   ⚠️  Test PDF not found, creating mock file...")
        with open(test_pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF")
    
    try:
        with open(test_pdf_path, "rb") as f:
            files = {"file": ("test_claim.pdf", f, "application/pdf")}
            response = requests.post("http://localhost:8000/upload/claim", files=files)
        
        if response.status_code == 200:
            data = response.json()
            claim_id = data["claim_id"]
            print(f"   ✅ Document uploaded successfully: {claim_id}")
            return claim_id
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Upload error: {str(e)}")
        return None

def test_claim_analysis(claim_id):
    """Test claim analysis functionality"""
    print(f"\n🔍 Testing claim analysis for {claim_id}...")
    
    # Wait for background processing
    print("   ⏳ Waiting for background processing...")
    time.sleep(5)
    
    try:
        # Get claims list
        response = requests.get("http://localhost:8000/claims")
        if response.status_code == 200:
            data = response.json()
            if data["claims"]:
                claim = data["claims"][0]
                print(f"   ✅ Analysis completed:")
                print(f"      - Severity: {claim['severity']}/10")
                print(f"      - Complexity: {claim['complexity']}")
                print(f"      - Suggested Team: {claim['suggested_team']}")
                print(f"      - Flags: {', '.join(claim['flags'])}")
                return True
            else:
                print("   ❌ No processed claims found")
                return False
        else:
            print(f"   ❌ Failed to get claims: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Analysis error: {str(e)}")
        return False

def test_question_answering(claim_id):
    """Test question answering functionality"""
    print(f"\n❓ Testing question answering for {claim_id}...")
    
    try:
        question_data = {"question": "What is the claim amount?"}
        response = requests.post(f"http://localhost:8000/claims/{claim_id}/ask_question", json=question_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Question answered:")
            print(f"      - Question: {data['question']}")
            print(f"      - Answer: {data['answer']}")
            return True
        else:
            print(f"   ❌ Question answering failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Question answering error: {str(e)}")
        return False

def test_claim_reassignment(claim_id):
    """Test claim reassignment functionality"""
    print(f"\n🔄 Testing claim reassignment for {claim_id}...")
    
    try:
        reassign_data = {"new_team": "Special Investigation Unit"}
        response = requests.post(f"http://localhost:8000/claims/{claim_id}/reassign", json=reassign_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Claim reassigned:")
            print(f"      - New Team: {data['new_team']}")
            print(f"      - Status: {data['status']}")
            return True
        else:
            print(f"   ❌ Reassignment failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Reassignment error: {str(e)}")
        return False

def test_landingai_integration():
    """Test LandingAI MCP server integration"""
    print("\n🤖 Testing LandingAI MCP server integration...")
    
    try:
        # Test LandingAI status
        response = requests.get("http://localhost:8000/landingai/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ LandingAI integration status:")
            print(f"      - Available: {data['available']}")
            print(f"      - Status: {data['status']}")
            return True
        else:
            print(f"   ❌ LandingAI status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ LandingAI integration error: {str(e)}")
        return False

def main():
    print("🧪 Financial Agent Complete Integration Test")
    print("=" * 50)
    
    # Test 1: Service Health
    if not test_service_health():
        print("\n❌ Service health check failed. Please ensure all services are running.")
        return
    
    # Test 2: Document Upload
    claim_id = test_document_upload()
    if not claim_id:
        print("\n❌ Document upload test failed.")
        return
    
    # Test 3: Claim Analysis
    if not test_claim_analysis(claim_id):
        print("\n❌ Claim analysis test failed.")
        return
    
    # Test 4: Question Answering
    if not test_question_answering(claim_id):
        print("\n❌ Question answering test failed.")
        return
    
    # Test 5: Claim Reassignment
    if not test_claim_reassignment(claim_id):
        print("\n❌ Claim reassignment test failed.")
        return
    
    # Test 6: LandingAI Integration
    if not test_landingai_integration():
        print("\n❌ LandingAI integration test failed.")
        return
    
    print("\n" + "=" * 50)
    print("🎉 ALL INTEGRATION TESTS PASSED!")
    print("=" * 50)
    
    print("\n📋 Integration Summary:")
    print("   ✅ Service Health: All services running")
    print("   ✅ Document Upload: PDF processing working")
    print("   ✅ AI Analysis: Claim scoring and team assignment")
    print("   ✅ Question Answering: Document Q&A functionality")
    print("   ✅ Claim Reassignment: Team management")
    print("   ✅ LandingAI Integration: MCP server communication")
    
    print("\n🌐 Access Points:")
    print("   Frontend:           http://localhost:5173")
    print("   Enhanced Claims API: http://localhost:8000")
    print("   LandingAI MCP:      http://localhost:8001")
    print("   Inkeep UI:          http://localhost:3000")
    print("   Manage UI:          http://localhost:2001")
    
    print("\n✨ The Financial Agent integration is fully operational!")

if __name__ == "__main__":
    main()
