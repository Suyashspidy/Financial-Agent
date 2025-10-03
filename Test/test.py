from landingai_ade.types import ExtractResponse, ParseResponse
import os
from landingai_ade import LandingAIADE
from dotenv import load_dotenv
from landingai_ade.lib import pydantic_to_json_schema
from pydantic import BaseModel, Field
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

# Use an absolute path to the document relative to this script's directory
script_dir = Path(__file__).parent
document_path = str(script_dir / "4pages.pdf")
if not Path(document_path).exists():
    raise FileNotFoundError(f"Document not found at {document_path}")
model_to_use="dpt-2-latest"
response = parse_document(client,document_path, model_to_use)
print(response)

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
