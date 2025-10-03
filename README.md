# Due Diligence Copilot

A Python-based AI-powered document analysis system for financial due diligence. Automatically ingests, extracts, and indexes financial documents, providing intelligent Q&A capabilities with full citation tracking and audit logging.

## 🎯 Features

- **Automated Document Ingestion**: Monitors and processes PDF/DOCX financial documents
- **Intelligent Extraction**: Uses LandingAI ADE to extract structured fields, tables, and text with citations
- **Live Indexing**: Pathway-based real-time indexing for instant document updates
- **Natural Language Q&A**: Ask questions and get answers with source citations
- **Risk Detection**: Automatic scanning for indemnity clauses, liabilities, and other risk factors
- **Clause Search**: Find specific contract clauses (termination, warranty, compliance, etc.)
- **Audit Logging**: Complete audit trail of all queries and responses
- **Modular Design**: Easy to extend for KYC, claims, or compliance use cases

## 📋 Requirements

- Python 3.8+
- LandingAI Vision Agent API Key
- OpenAI API Key (optional, for enhanced Q&A)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
cd Financial-Agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# Required: VISION_AGENT_API_KEY
# Optional: OPENAI_API_KEY
```

### 3. Add Documents

Place your financial documents (PDF or DOCX) in the documents folder:

```bash
# The application will create this folder automatically
# Default location: Financial-Agent/data/financial_docs/
```

### 4. Run the Application

```bash
# Interactive mode (default)
python due_diligence_copilot.py

# Or explicitly
python due_diligence_copilot.py interactive

# Command-line mode examples
python due_diligence_copilot.py ask "What are the payment terms?"
python due_diligence_copilot.py clause indemnity
python due_diligence_copilot.py risk
python due_diligence_copilot.py stats
```

## 💡 Usage Examples

### Interactive Mode

```
> What are the termination clauses in the contract?
> clause indemnity
> risk
> stats
> refresh
> quit
```

### Command-Line Mode

```bash
# Ask a question
python due_diligence_copilot.py ask "What are the indemnity clauses?"

# Find specific clause types
python due_diligence_copilot.py clause indemnity
python due_diligence_copilot.py clause termination today

# Scan for risks
python due_diligence_copilot.py risk

# View statistics
python due_diligence_copilot.py stats
```

## 📁 Project Structure

```
Financial-Agent/
├── config.py                      # Configuration management
├── document_extractor.py          # LandingAI ADE integration
├── document_ingestion.py          # Pathway-based ingestion & indexing
├── qa_workflow.py                 # Q&A and search functionality
├── audit_logger.py                # Audit logging system
├── due_diligence_copilot.py      # Main application
├── requirements.txt               # Python dependencies
├── .env.example                   # Example environment configuration
├── README.md                      # This file
│
├── data/
│   └── financial_docs/            # Place your documents here
│
├── index_data/
│   └── index.json                 # Document index (auto-generated)
│
└── logs/
    ├── query_log.jsonl            # Query audit log
    ├── risk_log.jsonl             # Risk scan log
    └── audit_summary.csv          # CSV audit summary
```

## 🔧 Core Modules

### config.py
Central configuration management for API keys, directories, and system settings.

### document_extractor.py
- Interfaces with LandingAI ADE Python SDK
- Extracts structured data from documents
- Generates answers with citations
- Identifies risk indicators

### document_ingestion.py
- Monitors document folder for changes
- Processes documents and extracts chunks
- Creates and manages Pathway indexes
- Enables fast document search

### qa_workflow.py
- Handles natural language queries
- Searches indexed documents
- Finds specific clause types
- Performs risk assessments
- Ensures all answers include evidence

### audit_logger.py
- Logs all queries and responses
- Tracks document access patterns
- Maintains audit trail for compliance
- Provides usage statistics
- Exports audit reports

### due_diligence_copilot.py
Main application providing CLI interface for:
- Document indexing
- Q&A sessions
- Clause searches
- Risk scanning
- Statistics viewing

## 🎨 Key Workflows

### 1. Document Processing Workflow

```
New Document → Extract with LandingAI ADE → Create Chunks → Index with Pathway → Ready for Query
```

### 2. Q&A Workflow

```
User Question → Search Index → Find Relevant Chunks → Generate Answer → Return with Citations → Log for Audit
```

### 3. Risk Scanning Workflow

```
Scan Request → For Each Document → Check Risk Keywords → Extract Relevant Sections → Flag Risks → Log Results
```

## 📊 Output Examples

### Q&A Response
```
Question: What are the payment terms?

Answer:
[1] Payment shall be made within 30 days of invoice date. Late payments 
    subject to 1.5% monthly interest...

📚 Citations (3):
  [1] contract_2024.pdf - Page 5
      "Payment shall be made within 30 days..."
  
  [2] agreement_jan2024.pdf - Page 3
      "Net 30 payment terms apply..."

✓ Query logged for audit
```

### Risk Scan Output
```
🚨 FLAGGED RISKS:

📄 service_agreement.pdf
   3 risk(s) identified:

   🔴 INDEMNITY
      The agreement contains broad indemnification clauses requiring the 
      service provider to indemnify against all claims...
      📍 Page 12

   🔴 LIABILITY
      Limited liability cap of $50,000 for all damages...
      📍 Page 14
```

## 🔐 Security & Compliance

- **Audit Logging**: Every query is logged with timestamp, user, and documents accessed
- **Citation Tracking**: All answers include source references
- **Evidence Required**: System validates that answers have supporting evidence
- **Audit Exports**: Export audit trails for compliance reviews

## 🛠️ Extending the System

The modular design allows easy extension:

### Add Custom Risk Keywords

```python
custom_keywords = ["force majeure", "arbitration", "jurisdiction"]
copilot.scan_risks(risk_keywords=custom_keywords)
```

### Create Custom Workflows

```python
from document_ingestion import DocumentIngestionPipeline
from qa_workflow import DueDiligenceQA

# Create custom pipeline
pipeline = DocumentIngestionPipeline()
qa = DueDiligenceQA(pipeline)

# Implement custom logic
def find_compliance_issues():
    return qa.find_contracts_with_clause("compliance")
```

### Add New Document Types

Extend `document_ingestion.py` to support additional formats:

```python
supported_extensions = ['.pdf', '.docx', '.doc', '.txt', '.html']
```

## 📝 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VISION_AGENT_API_KEY` | LandingAI API key (required) | - |
| `OPENAI_API_KEY` | OpenAI API key (optional) | - |
| `ENDPOINT_HOST` | LandingAI endpoint | `https://api.va.landing.ai` |
| `MODEL_NAME` | Document parsing model | `dpt-2-latest` |
| `PATHWAY_REFRESH_INTERVAL` | Index refresh interval (seconds) | `5` |
| `TOP_K_CHUNKS` | Number of chunks to consider | `8` |

## 🐛 Troubleshooting

### No Documents Found
- Ensure documents are in the correct folder: `data/financial_docs/`
- Supported formats: PDF, DOCX, DOC
- Check file permissions

### API Key Errors
- Verify `.env` file exists and contains valid API keys
- Check API key format (no quotes, no extra spaces)
- Ensure you have API credits/access

### Import Errors
- Install all requirements: `pip install -r requirements.txt`
- Check Python version: `python --version` (3.8+ required)

### Index Not Updating
- Use `refresh` command in interactive mode
- Check if documents were actually added/changed
- Verify write permissions to `index_data/` folder

## 🤝 Use Cases

1. **Contract Review**: Analyze contracts for specific clauses and obligations
2. **Risk Assessment**: Identify potential risks across multiple agreements
3. **Due Diligence**: Quick analysis of acquisition targets' documents
4. **Compliance Checks**: Find regulatory compliance clauses
5. **KYC Analysis**: Process customer documentation
6. **Claims Processing**: Extract relevant information from claims documents

## 📖 API Integration Examples

### Using as a Library

```python
from due_diligence_copilot import DueDiligenceCopilot

# Initialize
copilot = DueDiligenceCopilot()

# Index documents
copilot.index_documents()

# Ask questions programmatically
copilot.ask_question("What are the termination clauses?")

# Find specific clauses
results = copilot.find_clauses("indemnity")

# Scan for risks
risk_report = copilot.scan_risks()

# View statistics
stats = copilot.show_statistics()
```

## 🔄 Maintenance

### Clear Old Logs

```python
from audit_logger import AuditLogger

logger = AuditLogger()
logger.clear_old_logs(days_to_keep=90)
```

### Export Audit Trail

```python
logger.export_audit_trail(
    output_file="audit_2025_Q1.json",
    start_date="2025-01-01",
    end_date="2025-03-31"
)
```

## 📜 License

This project uses open-source Python tools, LandingAI ADE SDK, and Pathway SDK.

## 🙏 Acknowledgments

- **LandingAI ADE**: Document parsing and extraction
- **Pathway**: Real-time data indexing
- **OpenAI**: Enhanced Q&A capabilities

## 📞 Support

For issues, questions, or contributions:
1. Check troubleshooting section above
2. Review error messages in console output
3. Check audit logs for detailed information

---

**Built for Hack with Bay - Financial Agents Challenge** 🚀
