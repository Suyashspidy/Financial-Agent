from landingai_ade.types import ExtractResponse, ParseResponse
import os
import requests
import json
from landingai_ade import LandingAIADE
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional
load_dotenv()
os.environ["ENDPOINT_HOST"] = "https://api.va.landing.ai"

# Ensure API key is available; provide an actionable error early if missing
api_key = os.getenv("VISION_AGENT_API_KEY")
if not api_key:
    raise RuntimeError(
        "Missing VISION_AGENT_API_KEY. Create a .env with VISION_AGENT_API_KEY=your_key"
    )

client = LandingAIADE(
    apikey=api_key,
)

# Pydantic model for policy expiration date extraction
class PolicyInfo(BaseModel):
    policy_expiration_date: Optional[str] = Field(
        description="The policy expiration date from the document",
        default=None
    )
    policy_number: Optional[str] = Field(
        description="The policy number if available",
        default=None
    )
    effective_date: Optional[str] = Field(
        description="The policy effective date if available",
        default=None
    )




def parse_document(client, document_path, model_to_use):
    """Parse document to extract text chunks for further processing"""
    response = client.parse(
        # support document as File or document_url as local path/remote url
        document_url=document_path,
        model=model_to_use
    )
    return response


def extract_document_direct_api(document_path, schema_model, model_to_use="extract-latest"):
    """Extract structured data from document using direct ADE Extract API"""
    try:
        # Convert Pydantic model to JSON schema
        json_schema = pydantic_to_json_schema(schema_model)
        
        # API endpoint
        url = "https://api.va.landing.ai/v1/ade/extract"
        
        # Headers
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Prepare the request
        with open(document_path, 'rb') as file:
            files = {
                "markdown": file,
                "schema": (None, json.dumps(json_schema), "application/json")
            }
            
            # Add model parameter if specified
            data = {}
            if model_to_use:
                data["model"] = model_to_use
            
            # Send the request
            response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error during extraction: {e}")
        return None

# Use an absolute path to the document relative to this script's directory
script_dir = Path(__file__).parent
document_path = str(script_dir / "acordform.pdf")
if not Path(document_path).exists():
    raise FileNotFoundError(f"Document not found at {document_path}")

print("=" * 60)
print("DOCUMENT PARSING")
print("=" * 60)
model_to_use = "dpt-2-latest"
response = parse_document(client, document_path, model_to_use)
print("Parse response received successfully")
print(f"Number of chunks: {len(response.chunks) if hasattr(response, 'chunks') else 'N/A'}")

print("\n" + "=" * 60)
print("POLICY EXPIRATION DATE EXTRACTION")
print("=" * 60)

# Extract policy information using the ADE Extract API
extract_response = extract_document_direct_api(document_path, PolicyInfo, "extract-latest")

if extract_response:
    print("Extraction successful!")
    print(f"Extracted data: {extract_response.get('extraction', {})}")
    
    # Parse the extracted data into our Pydantic model
    try:
        extraction_data = extract_response.get('extraction', {})
        policy_info = PolicyInfo(**extraction_data)
        print("\nStructured Policy Information:")
        print(f"Policy Expiration Date: {policy_info.policy_expiration_date}")
        print(f"Policy Number: {policy_info.policy_number}")
        print(f"Effective Date: {policy_info.effective_date}")
        
        # Also show metadata if available
        if 'metadata' in extract_response:
            metadata = extract_response['metadata']
            print(f"\nExtraction Metadata:")
            print(f"Duration: {metadata.get('duration_ms', 'N/A')} ms")
            print(f"Credit Usage: {metadata.get('credit_usage', 'N/A')}")
            print(f"Job ID: {metadata.get('job_id', 'N/A')}")
            
    except Exception as e:
        print(f"Error parsing extracted data: {e}")
        print(f"Raw extraction: {extract_response.get('extraction', {})}")
else:
    print("Extraction failed!")
=======
def extract_policy_exp(text):
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

# Use an absolute path to the document relative to this script's directory
script_dir = Path(__file__).parent
document_path = str(script_dir / "accord-form.pdf")
if not Path(document_path).exists():
    raise FileNotFoundError(f"Document not found at {document_path}")
model_to_use="dpt-2-latest"
response = parse_document(client,document_path, model_to_use)
print("Full response:")
print(response)
print("\n" + "="*50 + "\n")

# Get markdown response
markdown_text = str(response)
print("Markdown Response:")
print(markdown_text)
print("\n" + "="*50 + "\n")

# Extract Policy Exp
policy_exp = extract_policy_exp(markdown_text)
if policy_exp:
    print(f"Policy Exp Found: {policy_exp}")
else:
    print("Policy Exp field not found")

# Save to file
output_file = script_dir / "response_output.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("Markdown Response:\n")
    f.write(markdown_text)
    f.write("\n\n" + "="*50 + "\n\n")
    f.write(f"Policy Exp: {policy_exp if policy_exp else 'Not found'}\n")
print(f"Response saved to: {output_file}")