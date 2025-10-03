#!/usr/bin/env python3
"""
Claims Triage Agent - Complete Workflow Demo
Demonstrates the full integration between frontend and backend
"""

import requests
import time
import webbrowser
from pathlib import Path

def main():
    print("🚀 Claims Triage Agent - Complete Integration Demo")
    print("=" * 60)
    
    # Configuration
    API_BASE_URL = "http://localhost:8000"
    FRONTEND_URL = "http://localhost:5173"
    
    print("📋 SYSTEM STATUS:")
    print(f"   🌐 Frontend: {FRONTEND_URL}")
    print(f"   🔧 Backend API: {API_BASE_URL}")
    print(f"   📚 API Documentation: {API_BASE_URL}/docs")
    
    # Check if both services are running
    print("\n🔍 Checking service status...")
    
    try:
        # Check backend
        api_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if api_response.status_code == 200:
            print("   ✅ Backend API: Running")
        else:
            print("   ❌ Backend API: Not responding")
            return
    except:
        print("   ❌ Backend API: Not accessible")
        return
    
    try:
        # Check frontend
        frontend_response = requests.get(FRONTEND_URL, timeout=5)
        if frontend_response.status_code == 200:
            print("   ✅ Frontend: Running")
        else:
            print("   ❌ Frontend: Not responding")
            return
    except:
        print("   ❌ Frontend: Not accessible")
        return
    
    print("\n🎯 WORKFLOW DEMONSTRATION:")
    print("=" * 40)
    
    # Step 1: Upload a claim
    print("\n1️⃣ Uploading a test claim...")
    pdf_path = Path("test_claim.pdf")
    if pdf_path.exists():
        with open(pdf_path, 'rb') as f:
            files = {'file': ('test_claim.pdf', f, 'application/pdf')}
            response = requests.post(f"{API_BASE_URL}/upload/claim", files=files)
        
        if response.status_code == 200:
            data = response.json()
            claim_id = data['claim_id']
            print(f"   ✅ Claim uploaded: {claim_id}")
        else:
            print("   ❌ Upload failed")
            return
    else:
        print("   ❌ Test PDF not found")
        return
    
    # Step 2: Wait for processing
    print("\n2️⃣ Processing claim (AI analysis)...")
    print("   ⏳ Waiting for background processing...")
    time.sleep(5)
    
    # Step 3: Retrieve processed claim
    print("\n3️⃣ Retrieving processed claim...")
    response = requests.get(f"{API_BASE_URL}/claims")
    if response.status_code == 200:
        data = response.json()
        if data['claims']:
            claim = data['claims'][0]
            print(f"   📄 Claim ID: {claim['id']}")
            print(f"   🎯 Severity Score: {claim['severity']}/10")
            print(f"   📊 Complexity: {claim['complexity']}")
            print(f"   👥 Suggested Team: {claim['suggested_team']}")
            print(f"   🚩 Risk Flags: {', '.join(claim['flags'])}")
            print(f"   📅 Upload Date: {claim['upload_date']}")
        else:
            print("   ❌ No processed claims found")
            return
    else:
        print("   ❌ Failed to retrieve claims")
        return
    
    # Step 4: Demonstrate reassignment
    print("\n4️⃣ Testing claim reassignment...")
    new_team = "Special Investigation Unit"
    response = requests.post(
        f"{API_BASE_URL}/claims/{claim_id}/reassign",
        json={"new_team": new_team}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Claim reassigned to: {data['new_team']}")
    else:
        print("   ❌ Reassignment failed")
    
    # Step 5: Open frontend
    print("\n5️⃣ Opening frontend application...")
    print(f"   🌐 Opening: {FRONTEND_URL}")
    
    try:
        webbrowser.open(FRONTEND_URL)
        print("   ✅ Frontend opened in browser")
    except:
        print("   ⚠️  Could not open browser automatically")
        print(f"   📝 Please manually open: {FRONTEND_URL}")
    
    print("\n" + "=" * 60)
    print("🎉 INTEGRATION DEMO COMPLETE!")
    print("=" * 60)
    
    print("\n📋 WHAT YOU CAN DO NOW:")
    print("   1. 🌐 Visit the frontend at http://localhost:5173")
    print("   2. 📤 Upload PDF files using drag & drop")
    print("   3. 📊 View AI-powered analysis results")
    print("   4. 🔄 Reassign claims to different teams")
    print("   5. 📚 Check API docs at http://localhost:8000/docs")
    
    print("\n🔧 TECHNICAL DETAILS:")
    print("   • Frontend: React + Vite + Tailwind CSS")
    print("   • Backend: FastAPI + Python")
    print("   • AI Analysis: Simulated with realistic scoring")
    print("   • File Processing: PDF upload with background analysis")
    print("   • CORS: Configured for localhost development")
    
    print("\n✨ The Claims Triage Agent is fully operational!")

if __name__ == "__main__":
    main()
