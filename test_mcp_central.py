#!/usr/bin/env python3
"""
Financial Agent MCP Central Frontend Test
Tests the complete architecture: UI -> MCP Server -> Landing AI, Inkeep, LLM -> Pathway -> Response
"""

import requests
import time
import json
from pathlib import Path

def test_mcp_central_health():
    """Test MCP Central Server health and all connected services"""
    print("🔍 Testing MCP Central Server health...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ MCP Central Server: {data['status']}")
            print(f"   📊 Connected Services:")
            
            services = data.get("connected_services", {})
            all_healthy = True
            
            for service_name, service_info in services.items():
                status = service_info.get("status", "unknown")
                if status == "healthy":
                    print(f"      ✅ {service_name}: {status}")
                else:
                    print(f"      ❌ {service_name}: {status}")
                    all_healthy = False
            
            return all_healthy
        else:
            print(f"   ❌ MCP Central Server: Unhealthy (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ MCP Central Server: Not accessible ({str(e)})")
        return False

def test_document_upload_pipeline():
    """Test Step 1: UI -> MCP Server document upload"""
    print("\n📤 Testing Step 1: Document Upload (UI -> MCP Server)...")
    
    # Create a test PDF file if it doesn't exist
    test_pdf_path = Path("test_claim.pdf")
    if not test_pdf_path.exists():
        print("   ⚠️  Test PDF not found, creating mock file...")
        with open(test_pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF")
    
    try:
        with open(test_pdf_path, "rb") as f:
            files = {"file": ("test_claim.pdf", f, "application/pdf")}
            response = requests.post("http://localhost:8000/upload/document", files=files)
        
        if response.status_code == 200:
            data = response.json()
            document_id = data["document_id"]
            print(f"   ✅ Document uploaded successfully: {document_id}")
            print(f"   📋 Next step: {data['next_step']}")
            return document_id
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Upload error: {str(e)}")
        return None

def test_landingai_action(document_id):
    """Test Step 2: Landing AI -> MCP Server action"""
    print(f"\n🤖 Testing Step 2: Landing AI Action for {document_id}...")
    
    try:
        payload = {
            "document_id": document_id,
            "analysis_type": "comprehensive"
        }
        response = requests.post("http://localhost:8000/landingai/action", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Landing AI action completed: {data['status']}")
            print(f"   📋 Next step: {data['next_step']}")
            return True
        else:
            print(f"   ❌ Landing AI action failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Landing AI action error: {str(e)}")
        return False

def test_llm_processing():
    """Test Step 3: MCP Server -> LLM processing"""
    print("\n🧠 Testing Step 3: LLM Processing...")
    
    try:
        payload = {
            "prompt": "Analyze this insurance claim document for risk assessment",
            "context": "Insurance claim processing"
        }
        response = requests.post("http://localhost:8000/llm/process", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ LLM processing completed: {data['status']}")
            print(f"   📋 Next step: {data['next_step']}")
            print(f"   💭 LLM Output: {data['llm_output'][:100]}...")
            return True
        else:
            print(f"   ❌ LLM processing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ LLM processing error: {str(e)}")
        return False

def test_pathway_refinement():
    """Test Step 4: LLM -> Pathway refinement"""
    print("\n🔄 Testing Step 4: Pathway Refinement...")
    
    try:
        payload = {
            "content": "This is a standard insurance claim requiring general processing",
            "refinement_type": "enhance"
        }
        response = requests.post("http://localhost:8000/pathway/refine", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Pathway refinement completed: {data['status']}")
            print(f"   📋 Next step: {data['next_step']}")
            print(f"   ✨ Refined Content: {data['refined_content'][:100]}...")
            return True
        else:
            print(f"   ❌ Pathway refinement failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Pathway refinement error: {str(e)}")
        return False

def test_complete_pipeline(document_id):
    """Test complete processing pipeline"""
    print(f"\n🎯 Testing Complete Pipeline for {document_id}...")
    
    try:
        response = requests.post(f"http://localhost:8000/process/complete?document_id={document_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Complete pipeline executed successfully!")
            print(f"   📄 Document ID: {data['document_id']}")
            print(f"   🔍 Analysis: {data.get('analysis', {}).get('severity', 'N/A')}/10 severity")
            print(f"   🧠 LLM Processing: {data.get('llm_processing', 'N/A')[:50]}...")
            print(f"   ✨ Refined Content: {data.get('refined_content', 'N/A')[:50]}...")
            return True
        else:
            print(f"   ❌ Complete pipeline failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Complete pipeline error: {str(e)}")
        return False

def test_inkeep_integration():
    """Test Inkeep agent integration"""
    print("\n🧠 Testing Inkeep Agent Integration...")
    
    try:
        payload = {
            "action_type": "analyze_claim",
            "parameters": {"claim_id": "test-claim-123"},
            "agent_id": "claims-agent-001"
        }
        response = requests.post("http://localhost:8000/inkeep/action", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Inkeep action completed: {data['status']}")
            if 'session_id' in data:
                print(f"   📋 Session ID: {data['session_id']}")
            return True
        else:
            print(f"   ❌ Inkeep action failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Inkeep integration error: {str(e)}")
        return False

def test_question_answering(document_id):
    """Test question answering system"""
    print(f"\n❓ Testing Question Answering for {document_id}...")
    
    try:
        payload = {
            "document_id": document_id,
            "question": "What is the risk level of this claim?",
            "context": "Risk assessment"
        }
        response = requests.post("http://localhost:8000/ask/question", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Question answered successfully!")
            print(f"   ❓ Question: {data['question']}")
            print(f"   💡 Answer: {data['answer'][:100]}...")
            print(f"   🎯 Confidence: {data['confidence']}")
            return True
        else:
            print(f"   ❌ Question answering failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Question answering error: {str(e)}")
        return False

def main():
    print("🧪 Financial Agent MCP Central Frontend Test")
    print("=" * 60)
    print("Architecture: UI -> MCP Server -> Landing AI, Inkeep, LLM -> Pathway -> Response")
    print("=" * 60)
    
    # Test 1: MCP Central Server Health
    if not test_mcp_central_health():
        print("\n❌ MCP Central Server health check failed. Please ensure all services are running.")
        return
    
    # Test 2: Document Upload Pipeline (Step 1)
    document_id = test_document_upload_pipeline()
    if not document_id:
        print("\n❌ Document upload test failed.")
        return
    
    # Test 3: Landing AI Action (Step 2)
    if not test_landingai_action(document_id):
        print("\n❌ Landing AI action test failed.")
        return
    
    # Test 4: LLM Processing (Step 3)
    if not test_llm_processing():
        print("\n❌ LLM processing test failed.")
        return
    
    # Test 5: Pathway Refinement (Step 4)
    if not test_pathway_refinement():
        print("\n❌ Pathway refinement test failed.")
        return
    
    # Test 6: Complete Pipeline
    if not test_complete_pipeline(document_id):
        print("\n❌ Complete pipeline test failed.")
        return
    
    # Test 7: Inkeep Integration
    if not test_inkeep_integration():
        print("\n❌ Inkeep integration test failed.")
        return
    
    # Test 8: Question Answering
    if not test_question_answering(document_id):
        print("\n❌ Question answering test failed.")
        return
    
    print("\n" + "=" * 60)
    print("🎉 ALL MCP CENTRAL FRONTEND TESTS PASSED!")
    print("=" * 60)
    
    print("\n📋 Architecture Implementation Summary:")
    print("   ✅ Step 1: UI -> MCP Server (Document Upload)")
    print("   ✅ Step 2: Landing AI -> MCP Server (Action)")
    print("   ✅ Step 3: MCP Server -> LLM (Processing)")
    print("   ✅ Step 4: LLM -> Pathway (Refinement)")
    print("   ✅ Step 5: Pathway -> MCP Server (Response)")
    print("   ✅ Step 6: MCP Server -> UI (Answers for Display)")
    print("   ✅ Inkeep Agent Integration (Google API)")
    print("   ✅ Question Answering System")
    
    print("\n🌐 Access Points:")
    print("   MCP Central Server:    http://localhost:8000  (Main Frontend)")
    print("   Frontend (UI):         http://localhost:5173")
    print("   LandingAI MCP Server:  http://localhost:8001")
    print("   Inkeep UI:             http://localhost:3000")
    print("   Manage UI:             http://localhost:2001")
    
    print("\n✨ The MCP Central Frontend is fully operational!")
    print("🎯 MCP Server successfully represents and orchestrates all components!")

if __name__ == "__main__":
    main()
