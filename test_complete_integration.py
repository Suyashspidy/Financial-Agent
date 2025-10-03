"""
Comprehensive Integration Test for Financial Agent with LandingAI
Tests the complete workflow: Frontend -> Enhanced Claims API -> LandingAI MCP Server
"""

import requests
import time
import os
import webbrowser
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

# Configuration
ENHANCED_API_URL = "http://localhost:8000"
LANDINGAI_MCP_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:5173"
TEST_PDF_PATH = "integration_test_claim.pdf"

def create_test_claim_pdf(filename=TEST_PDF_PATH):
    """Create a comprehensive test PDF for integration testing"""
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Header
    c.drawString(100, 750, "INSURANCE CLAIM DOCUMENT")
    c.drawString(100, 730, "=" * 50)
    
    # Claim Information
    c.drawString(100, 700, "Claim ID: INT-TEST-2024-001")
    c.drawString(100, 680, "Policy Number: POL-123456-XYZ")
    c.drawString(100, 660, "Claimant: John Smith")
    c.drawString(100, 640, "Date of Loss: 2024-01-15")
    c.drawString(100, 620, "Reported Date: 2024-01-16")
    
    # Incident Details
    c.drawString(100, 580, "INCIDENT DETAILS:")
    c.drawString(100, 560, "Type: Vehicle Accident")
    c.drawString(100, 540, "Location: Highway 101, San Francisco, CA")
    c.drawString(100, 520, "Description: Rear-end collision during rush hour traffic.")
    c.drawString(100, 500, "The claimant was stopped at a red light when another vehicle")
    c.drawString(100, 480, "failed to stop and collided with the rear of the claimant's vehicle.")
    
    # Damage Assessment
    c.drawString(100, 440, "DAMAGE ASSESSMENT:")
    c.drawString(100, 420, "Vehicle: 2020 Honda Civic")
    c.drawString(100, 400, "Estimated Damage: $8,500")
    c.drawString(100, 380, "Repair Shop: AutoCare Plus")
    c.drawString(100, 360, "Inspection Date: 2024-01-17")
    
    # Risk Factors
    c.drawString(100, 320, "RISK INDICATORS:")
    c.drawString(100, 300, "- High-value claim requiring expert review")
    c.drawString(100, 280, "- Potential fraud indicators detected")
    c.drawString(100, 260, "- Complex liability determination needed")
    c.drawString(100, 240, "- Litigation risk assessment required")
    
    # Additional Information
    c.drawString(100, 200, "ADDITIONAL NOTES:")
    c.drawString(100, 180, "This claim involves multiple parties and requires")
    c.drawString(100, 160, "comprehensive investigation. The claimant has")
    c.drawString(100, 140, "requested expedited processing due to urgent")
    c.drawString(100, 120, "financial circumstances.")
    
    c.save()
    print(f"✅ Test PDF created: {filename}")

def test_landingai_mcp_server():
    """Test LandingAI MCP Server availability and functionality"""
    print("\n🔍 Testing LandingAI MCP Server...")
    
    try:
        # Health check
        response = requests.get(f"{LANDINGAI_MCP_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ LandingAI MCP Server: {data['status']}")
            print(f"   📊 Extractor Available: {data.get('extractor_available', False)}")
            return True
        else:
            print(f"   ❌ LandingAI MCP Server: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ LandingAI MCP Server: {e}")
        return False

def test_enhanced_claims_api():
    """Test Enhanced Claims API availability and LandingAI integration"""
    print("\n🔍 Testing Enhanced Claims API...")
    
    try:
        # Health check
        response = requests.get(f"{ENHANCED_API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Enhanced Claims API: {data['status']}")
            print(f"   🤖 LandingAI Available: {data.get('landingai_available', False)}")
            return True
        else:
            print(f"   ❌ Enhanced Claims API: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Enhanced Claims API: {e}")
        return False

def test_frontend_accessibility():
    """Test frontend accessibility"""
    print("\n🔍 Testing Frontend Accessibility...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            if "Claims Triage Agent" in response.text:
                print("   ✅ Frontend: Accessible and loaded correctly")
                return True
            else:
                print("   ❌ Frontend: Content not as expected")
                return False
        else:
            print(f"   ❌ Frontend: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Frontend: {e}")
        return False

def test_document_upload_and_processing():
    """Test complete document upload and processing workflow"""
    print("\n📤 Testing Document Upload and Processing...")
    
    # Create test PDF
    create_test_claim_pdf()
    
    try:
        # Upload document
        with open(TEST_PDF_PATH, "rb") as f:
            files = {"file": (TEST_PDF_PATH, f, "application/pdf")}
            response = requests.post(f"{ENHANCED_API_URL}/upload/claim", files=files)
        
        if response.status_code == 200:
            data = response.json()
            claim_id = data["claim_id"]
            print(f"   ✅ Document uploaded: {claim_id}")
            print(f"   🤖 LandingAI Processing: {data.get('landingai_processing', False)}")
            
            # Wait for processing
            print("   ⏳ Waiting for LandingAI processing...")
            time.sleep(8)  # Give more time for LandingAI processing
            
            # Check processing status
            status_response = requests.get(f"{ENHANCED_API_URL}/claims/{claim_id}")
            if status_response.status_code == 200:
                claim_data = status_response.json()
                print(f"   📊 Severity: {claim_data['severity']}/10")
                print(f"   📈 Complexity: {claim_data['complexity']}")
                print(f"   👥 Team: {claim_data['suggested_team']}")
                print(f"   🚩 Flags: {', '.join(claim_data['flags'])}")
                if claim_data.get('confidence'):
                    print(f"   🎯 Confidence: {claim_data['confidence']:.2f}")
                if claim_data.get('risk_score'):
                    print(f"   ⚠️  Risk Score: {claim_data['risk_score']:.2f}")
                return True, claim_id
            else:
                print(f"   ❌ Failed to get claim status: {status_response.status_code}")
                return False, None
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Upload test failed: {e}")
        return False, None

def test_question_answering(claim_id):
    """Test question answering functionality"""
    print(f"\n❓ Testing Question Answering for Claim {claim_id}...")
    
    try:
        questions = [
            "What is the estimated damage amount?",
            "What type of incident occurred?",
            "Are there any risk indicators mentioned?"
        ]
        
        for question in questions:
            response = requests.post(f"{ENHANCED_API_URL}/claims/{claim_id}/ask_question", 
                                   json={"question": question})
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Q: {question}")
                print(f"   📝 A: {data['answer']['answer'][:100]}...")
            else:
                print(f"   ❌ Question failed: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"   ❌ Question answering failed: {e}")
        return False

def test_claim_reassignment(claim_id):
    """Test claim reassignment functionality"""
    print(f"\n🔄 Testing Claim Reassignment for {claim_id}...")
    
    try:
        response = requests.post(f"{ENHANCED_API_URL}/claims/{claim_id}/reassign", 
                               json={"new_team": "Special Investigation Unit"})
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Claim reassigned to: {data['new_team']}")
            return True
        else:
            print(f"   ❌ Reassignment failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Reassignment test failed: {e}")
        return False

def test_landingai_direct_integration():
    """Test direct integration with LandingAI MCP server"""
    print("\n🤖 Testing Direct LandingAI Integration...")
    
    try:
        # Test document analysis
        response = requests.post(f"{LANDINGAI_MCP_URL}/analyze_claim", 
                               json={"document_path": TEST_PDF_PATH, "analysis_type": "comprehensive"})
        
        if response.status_code == 200:
            data = response.json()
            analysis = data["data"]
            print(f"   ✅ LandingAI Analysis: Severity {analysis['severity']}/10")
            print(f"   📊 Complexity: {analysis['complexity']}")
            print(f"   👥 Suggested Team: {analysis['suggested_team']}")
            print(f"   🚩 Flags: {', '.join(analysis['flags'])}")
            return True
        else:
            print(f"   ❌ LandingAI analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ LandingAI integration test failed: {e}")
        return False

def open_frontend():
    """Open frontend in browser"""
    print(f"\n🌐 Opening Frontend: {FRONTEND_URL}")
    try:
        webbrowser.open(FRONTEND_URL)
        print("   ✅ Frontend opened in browser")
    except Exception as e:
        print(f"   ❌ Failed to open frontend: {e}")

def run_comprehensive_integration_test():
    """Run complete integration test suite"""
    print("🚀 Financial Agent - Comprehensive Integration Test")
    print("=" * 60)
    print("🎯 Testing: Frontend + Enhanced Claims API + LandingAI MCP Server")
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test individual components
    results["LandingAI MCP Server"] = test_landingai_mcp_server()
    results["Enhanced Claims API"] = test_enhanced_claims_api()
    results["Frontend Accessibility"] = test_frontend_accessibility()
    
    # Test integration workflows
    upload_success, claim_id = test_document_upload_and_processing()
    results["Document Upload & Processing"] = upload_success
    
    if claim_id:
        results["Question Answering"] = test_question_answering(claim_id)
        results["Claim Reassignment"] = test_claim_reassignment(claim_id)
    else:
        results["Question Answering"] = False
        results["Claim Reassignment"] = False
    
    results["Direct LandingAI Integration"] = test_landingai_direct_integration()
    
    # Open frontend
    open_frontend()
    
    # Print results summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    passed_count = 0
    total_count = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if passed:
            passed_count += 1
    
    print(f"\n🎯 Overall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 ALL TESTS PASSED! Complete integration is working!")
    elif passed_count >= total_count * 0.7:
        print("⚠️  Most tests passed. Some components may need attention.")
    else:
        print("❌ Multiple test failures. Check component configurations.")
    
    print("\n🌐 Access Points:")
    print(f"   Frontend: {FRONTEND_URL}")
    print(f"   Enhanced API: {ENHANCED_API_URL}")
    print(f"   LandingAI MCP: {LANDINGAI_MCP_URL}")
    print(f"   API Docs: {ENHANCED_API_URL}/docs")
    
    # Clean up test file
    if os.path.exists(TEST_PDF_PATH):
        os.remove(TEST_PDF_PATH)
        print(f"\n🧹 Cleaned up test file: {TEST_PDF_PATH}")

if __name__ == "__main__":
    run_comprehensive_integration_test()
