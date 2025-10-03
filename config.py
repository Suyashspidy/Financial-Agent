"""
Configuration module for Due Diligence Copilot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the Due Diligence Copilot"""
    
    # API Keys
    VISION_AGENT_API_KEY = os.getenv("VISION_AGENT_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # LandingAI Configuration
    ENDPOINT_HOST = os.getenv("ENDPOINT_HOST", "https://api.va.landing.ai")
    MODEL_NAME = os.getenv("MODEL_NAME", "dpt-2-latest")
    
    # Directory Configuration
    BASE_DIR = Path(__file__).parent
    DOCS_FOLDER = BASE_DIR / "data" / "financial_docs"
    AUDIT_LOG_FOLDER = BASE_DIR / "logs"
    INDEX_FOLDER = BASE_DIR / "index_data"
    
    # Pathway Configuration
    PATHWAY_REFRESH_INTERVAL = int(os.getenv("PATHWAY_REFRESH_INTERVAL", "5"))  # seconds
    
    # Q&A Configuration
    TOP_K_CHUNKS = int(os.getenv("TOP_K_CHUNKS", "8"))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.VISION_AGENT_API_KEY:
            errors.append("VISION_AGENT_API_KEY is required. Add it to your .env file")
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required for Q&A. Add it to your .env file")
        
        if errors:
            raise ValueError("\n".join(errors))
        
        # Create necessary directories
        cls.DOCS_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.AUDIT_LOG_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.INDEX_FOLDER.mkdir(parents=True, exist_ok=True)
        
        return True
    
    @classmethod
    def get_env_setup(cls):
        """Return environment setup string for LandingAI"""
        os.environ["ENDPOINT_HOST"] = cls.ENDPOINT_HOST
        return cls.ENDPOINT_HOST
