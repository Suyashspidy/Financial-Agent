from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile
from pathlib import Path
from landingai_ade import LandingAIADE
from dotenv import load_dotenv

load_dotenv()
os.environ["ENDPOINT_HOST"] = "https://api.va.landing.ai"

app = FastAPI(title="Document Parser API")

# Initialize client
api_key = os.getenv("VISION_AGENT_API_KEY")
if not api_key:
    raise RuntimeError("Missing VISION_AGENT_API_KEY")

client = LandingAIADE(apikey=api_key)

def parse_document(file_path: str, model: str = "dpt-2-latest"):
    """Parse document and return response"""
    response = client.parse(document_url=file_path, model=model)
    return response

def extract_policy_exp(text: str):
    """Extract Policy Exp from markdown text"""
    lines = text.split('\n')
    for line in lines:
        if 'policy exp' in line.lower():
            if ':' in line:
                return line.split(':', 1)[1].strip()
            elif '|' in line:
                parts = line.split('|')
                for i, part in enumerate(parts):
                    if 'policy exp' in part.lower() and i + 1 < len(parts):
                        return parts[i + 1].strip()
            return line.strip()
    return None

@app.post("/parse-document/")
async def parse_document_endpoint(file: UploadFile = File(...)):
    """Upload a document and get markdown response with Policy Exp extraction"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Parse document
        response = parse_document(temp_file_path)
        markdown_text = str(response)
        
        # Extract Policy Exp
        policy_exp = extract_policy_exp(markdown_text)
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        return {
            "filename": file.filename,
            "markdown_response": markdown_text,
            "policy_exp": policy_exp if policy_exp else "Not found"
        }
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Document Parser API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)