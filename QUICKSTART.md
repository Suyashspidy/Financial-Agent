# Quick Start Guide - Due Diligence Copilot

Get started with the Due Diligence Copilot in 5 minutes!

## Step 1: Install Dependencies

```bash
cd Financial-Agent
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your favorite text editor
# Windows:
notepad .env

# Linux/Mac:
nano .env
# or
vim .env
```

Add your LandingAI API key to the `.env` file:
```
VISION_AGENT_API_KEY=your_actual_api_key_here
```

Get your API key from: https://landing.ai/

## Step 3: Test Your Setup

```bash
python test_setup.py
```

If all tests pass, you're ready to go! ✓

## Step 4: Add Documents

Copy your financial documents (PDF or DOCX) to:
```
Financial-Agent/data/financial_docs/
```

For testing, you can use the sample document in `Test/4pages.pdf`:
```bash
# Windows
copy Test\4pages.pdf data\financial_docs\

# Linux/Mac
cp Test/4pages.pdf data/financial_docs/
```

## Step 5: Run the Copilot

### Interactive Mode (Recommended for First Time)

```bash
python due_diligence_copilot.py
```

Then try these commands:
```
> What is in this document?
> clause indemnity
> risk
> stats
> quit
```

### Command-Line Mode

```bash
# Ask a question
python due_diligence_copilot.py ask "What are the key terms?"

# Find clauses
python due_diligence_copilot.py clause indemnity

# Scan for risks
python due_diligence_copilot.py risk

# View statistics
python due_diligence_copilot.py stats
```

## Common Use Cases

### 1. Contract Analysis
```bash
python due_diligence_copilot.py ask "What are the payment terms in the contract?"
```

### 2. Risk Assessment
```bash
python due_diligence_copilot.py risk
```

### 3. Find Specific Clauses
```bash
# Find indemnity clauses
python due_diligence_copilot.py clause indemnity

# Find termination clauses
python due_diligence_copilot.py clause termination

# Find liability clauses
python due_diligence_copilot.py clause liability
```

### 4. Today's Documents
```bash
python due_diligence_copilot.py clause indemnity today
```

## Troubleshooting

### "VISION_AGENT_API_KEY is required"
- Make sure you created the `.env` file (not `.env.example`)
- Make sure you added your actual API key to the file
- No quotes needed around the API key

### "No documents found"
- Check that documents are in `data/financial_docs/` folder
- Supported formats: PDF, DOCX, DOC
- The folder will be created automatically on first run

### Import errors
```bash
pip install -r requirements.txt
```

### Module not found errors
- Make sure you're in the `Financial-Agent` directory
- Try running: `python -m pip install -r requirements.txt`

## What's Next?

1. **Explore the Interactive Mode**: Type `help` to see all commands
2. **Read the Full Documentation**: See `README.md` for detailed information
3. **Check the Logs**: View audit logs in `logs/` folder
4. **Customize Risk Keywords**: Modify risk detection in the code
5. **Extend for Your Use Case**: The system is modular and easy to extend

## Key Features to Try

- **Natural Language Q&A**: Ask any question about your documents
- **Citation Tracking**: Every answer includes source references
- **Risk Detection**: Automatic scanning for common risk factors
- **Clause Search**: Find specific types of clauses across all documents
- **Audit Logging**: Complete audit trail for compliance
- **Live Indexing**: Add new documents anytime, refresh with `refresh` command

## Example Session

```
$ python due_diligence_copilot.py

============================================================
      Due Diligence Copilot - Financial Document Analysis
============================================================
Initializing Due Diligence Copilot...
✓ Configuration validated
✓ Documents folder: Financial-Agent/data/financial_docs
✓ Logs folder: Financial-Agent/logs
✓ Index folder: Financial-Agent/index_data

============================================================
INDEXING DOCUMENTS
============================================================
Scanning directory: Financial-Agent/data/financial_docs
Found 1 documents to process
Processing document: contract.pdf
Extracted 25 chunks from contract.pdf

✓ Successfully indexed 25 chunks
✓ Total documents: 1

Indexed Documents:
  - contract.pdf (25 chunks)

============================================================
INTERACTIVE MODE
============================================================

Commands:
  ask <question>          - Ask a question
  clause <type>           - Find clauses
  risk                    - Scan for risks
  refresh                 - Refresh document index
  stats                   - Show statistics
  help                    - Show this help
  quit                    - Exit

============================================================

> What are the indemnity clauses?

============================================================
Q&A SESSION
============================================================
Question: What are the indemnity clauses?
------------------------------------------------------------

Answer:
[1] The Contractor shall indemnify and hold harmless the Company...

📚 Citations (1):
  [1] contract.pdf - Page 12
      "The Contractor shall indemnify and hold harmless..."

✓ Query logged for audit

> quit

Goodbye! 👋
```

## Support

For issues:
1. Check this guide
2. Run `python test_setup.py`
3. Review error messages carefully
4. Check the README.md for detailed troubleshooting

---

**Ready to analyze your documents? Let's go! 🚀**
