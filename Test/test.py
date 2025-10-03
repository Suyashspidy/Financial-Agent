from landingai_ade.types import ExtractResponse, ParseResponse
import os
from landingai_ade import LandingAIADE
from dotenv import load_dotenv
from pathlib import Path
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




def parse_document(client,document_path, model_to_use):
    response = client.parse(
        # support document as File or document_url as local path/remote url
        document_url=document_path,
        model=model_to_use
    )
    return response

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

# print(response.chunks)
# question = "What is the revenue for year 2024 in the confectionery segment?"

# # If your SDK has a built-in QA helper (per LandingAI tutorial), it will look like this:
# answer_resp = client.answer(
#     question=question,
#     parsed=response,           # pass the parse output so it can ground answers
#     top_k=8,                     # number of most relevant chunks to consider
#     with_citations=True,         # include page refs / chunk grounding
#     with_spans=True,             # include bbox spans for highlights
# )

# print("Answer:", answer_resp.answer_text)
# for cite in answer_resp.citations:
#     print(f"- Page {cite.page_index+1}, score={cite.score}, snippet={cite.text[:120]}")

# # 3) (Optional) Subsequent questions reuse the same parsed result without re-parsing
# follow_up = "Breakdown that 2024 confectionery revenue number by region if shown."
# follow_resp = client.answer(
#     question=follow_up,
#     parsed=response,
#     top_k=8,
#     with_citations=True,
# )
# print("Follow-up:", follow_resp.answer_text)
