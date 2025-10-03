# Financial Agent MCP Server

This MCP (Model Context Protocol) server provides AI-powered financial fraud detection and document processing capabilities.

## Architecture

The MCP server is organized into the following components:

### 📁 Document Ingestion (`document-ingestion/`)
- Handles incoming financial documents
- Supports multiple formats (PDF, CSV, Excel, JSON)
- Validates document structure and content
- Manages document metadata and indexing

### 📁 Document Conversion (`document-conversion/`)
- Converts documents to standardized formats
- Extracts text and structured data
- Handles OCR for scanned documents
- Normalizes data for AI processing

### 📁 AI Services (`ai-services/`)
- Core AI processing engine
- Natural language processing for financial text
- Pattern recognition and anomaly detection
- Integration with various AI models

### 📁 Fraud Detection (`fraud-detection/`)
- Specialized fraud detection algorithms
- Transaction analysis and scoring
- Risk assessment and alerting
- Compliance monitoring

## Features

- **Multi-format Document Support**: PDF, CSV, Excel, JSON, XML
- **Real-time Processing**: Stream processing for high-volume data
- **AI-Powered Analysis**: Machine learning models for fraud detection
- **Scalable Architecture**: Microservices-based design
- **RESTful API**: Easy integration with external systems
- **Comprehensive Logging**: Full audit trail and monitoring

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment variables in `.env`
3. Start the server: `python main.py`
4. Access API documentation at `http://localhost:8000/docs`

## API Endpoints

- `POST /ingest/document` - Upload and process documents
- `GET /analyze/{document_id}` - Get analysis results
- `POST /detect/fraud` - Run fraud detection on data
- `GET /health` - Health check endpoint

## Configuration

See `config.yaml` for detailed configuration options.

## License

MIT License - see LICENSE file for details.
