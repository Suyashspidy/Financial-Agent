"""
Test script to verify Due Diligence Copilot setup
Run this to check if all components are properly configured
"""
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        import pathway as pw
        print("✓ Pathway imported successfully")
    except ImportError as e:
        print(f"✗ Pathway import failed: {e}")
        return False
    
    try:
        from landingai_ade import LandingAIADE
        print("✓ LandingAI ADE imported successfully")
    except ImportError as e:
        print(f"✗ LandingAI ADE import failed: {e}")
        return False
    
    try:
        from pydantic import BaseModel
        print("✓ Pydantic imported successfully")
    except ImportError as e:
        print(f"✗ Pydantic import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ Python-dotenv imported successfully")
    except ImportError as e:
        print(f"✗ Python-dotenv import failed: {e}")
        return False
    
    return True

def test_config():
    """Test if configuration is valid"""
    print("\nTesting configuration...")
    try:
        from config import Config
        
        # Check if API key exists
        if not Config.VISION_AGENT_API_KEY:
            print("✗ VISION_AGENT_API_KEY not set in .env file")
            return False
        else:
            print("✓ VISION_AGENT_API_KEY found")
        
        # Check if directories can be created
        Config.validate()
        print("✓ Configuration validated")
        print(f"  - Docs folder: {Config.DOCS_FOLDER}")
        print(f"  - Logs folder: {Config.AUDIT_LOG_FOLDER}")
        print(f"  - Index folder: {Config.INDEX_FOLDER}")
        
        return True
        
    except ValueError as e:
        print(f"✗ Configuration validation failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during configuration test: {e}")
        return False

def test_modules():
    """Test if custom modules can be imported"""
    print("\nTesting custom modules...")
    try:
        from document_extractor import DocumentExtractor
        print("✓ DocumentExtractor imported successfully")
    except Exception as e:
        print(f"✗ DocumentExtractor import failed: {e}")
        return False
    
    try:
        from document_ingestion import DocumentIngestionPipeline
        print("✓ DocumentIngestionPipeline imported successfully")
    except Exception as e:
        print(f"✗ DocumentIngestionPipeline import failed: {e}")
        return False
    
    try:
        from qa_workflow import DueDiligenceQA
        print("✓ DueDiligenceQA imported successfully")
    except Exception as e:
        print(f"✗ DueDiligenceQA import failed: {e}")
        return False
    
    try:
        from audit_logger import AuditLogger
        print("✓ AuditLogger imported successfully")
    except Exception as e:
        print(f"✗ AuditLogger import failed: {e}")
        return False
    
    return True

def test_landingai_connection():
    """Test if LandingAI API can be reached"""
    print("\nTesting LandingAI connection...")
    try:
        from config import Config
        from landingai_ade import LandingAIADE
        
        Config.get_env_setup()
        client = LandingAIADE(apikey=Config.VISION_AGENT_API_KEY)
        print("✓ LandingAI client initialized successfully")
        print("  Note: Actual API connectivity will be tested when processing documents")
        return True
        
    except Exception as e:
        print(f"✗ LandingAI client initialization failed: {e}")
        return False

def check_sample_documents():
    """Check if there are any documents to process"""
    print("\nChecking for sample documents...")
    try:
        from config import Config
        
        docs_folder = Config.DOCS_FOLDER
        if not docs_folder.exists():
            print(f"ℹ No documents folder found (will be created on first run)")
            return True
        
        # Check for PDF/DOCX files
        pdf_files = list(docs_folder.glob("*.pdf"))
        docx_files = list(docs_folder.glob("*.docx"))
        
        total_files = len(pdf_files) + len(docx_files)
        
        if total_files == 0:
            print(f"ℹ No documents found in {docs_folder}")
            print(f"  Add PDF or DOCX files to this folder to get started")
        else:
            print(f"✓ Found {total_files} document(s):")
            for pdf in pdf_files:
                print(f"  - {pdf.name}")
            for docx in docx_files:
                print(f"  - {docx.name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error checking documents: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("Due Diligence Copilot - Setup Verification")
    print("="*60)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_imports()
    all_passed &= test_config()
    all_passed &= test_modules()
    all_passed &= test_landingai_connection()
    all_passed &= check_sample_documents()
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("="*60)
        print("\nYour setup is ready! You can now run:")
        print("  python due_diligence_copilot.py")
    else:
        print("✗ SOME TESTS FAILED")
        print("="*60)
        print("\nPlease fix the issues above before running the application.")
        print("\nCommon fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Create .env file: cp .env.example .env")
        print("3. Add your VISION_AGENT_API_KEY to .env file")
        sys.exit(1)

if __name__ == "__main__":
    main()
