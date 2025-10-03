import requests
from pathlib import Path

# API endpoint
API_URL = "http://localhost:8000/parse-document/"

# Test file path
script_dir = Path(__file__).parent
test_file = script_dir / "accord-form.pdf"

def test_api():
    """Test the document parsing API"""
    if not test_file.exists():
        print(f"Test file not found: {test_file}")
        return
    
    try:
        with open(test_file, "rb") as f:
            files = {"file": (test_file.name, f, "application/pdf")}
            response = requests.post(API_URL, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("API Response:")
            print(f"Filename: {result['filename']}")
            print(f"Policy Exp: {result['policy_exp']}")
            print("\nMarkdown Response:")
            print(result['markdown_response'])
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()