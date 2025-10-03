# Due Diligence Copilot MCP Server

Enhanced Due Diligence system with BDH (Dragon Hatchling) architecture and advanced fraud detection capabilities.

## 🧠 BDH Architecture Integration

This MCP server integrates the groundbreaking BDH (Dragon Hatchling) architecture based on Pathway's research paper: ["The Dragon Hatchling: The Missing Link BETWEEN THE TRANSFORMER AND MODELS OF THE BRAIN"](https://arxiv.org/pdf/2509.26507)

### Key BDH Features:
- **Biologically-inspired neural networks** with local graph dynamics
- **Hebbian learning** for synaptic plasticity simulation
- **Linear attention mechanisms** with RoPE (Rotary Position Embedding)
- **Interpretable neurons** with monosemanticity
- **Scale-free network topology** for efficient reasoning
- **Brain-like processing** with integrate-and-fire dynamics

## 🚀 Enhanced Features

### Document Analysis
- **Multi-format support**: PDF, DOCX, TXT, images
- **Intelligent extraction**: LandingAI ADE integration
- **BDH-enhanced analysis**: Neural processing for deeper insights
- **Real-time processing**: Sub-second document analysis

### Fraud Detection
- **Pattern-based detection**: Identifies suspicious patterns
- **Behavioral analysis**: Analyzes transaction behavior
- **BDH risk assessment**: Neural network-based risk scoring
- **Multi-factor analysis**: Combines multiple detection methods

### Q&A Enhancement
- **Enhanced responses**: BDH-powered answer enhancement
- **Confidence scoring**: Neural confidence assessment
- **Context analysis**: Deep understanding of document context
- **Citation tracking**: Full source attribution

## 📁 Project Structure

```
mcp-server/
├── bdh-architecture/          # BDH neural network implementation
│   ├── bdh_processor.py      # Core BDH processor for Due Diligence
│   └── __init__.py
├── api-endpoints/            # FastAPI REST endpoints
│   ├── api_endpoints.py      # Main API implementation
│   └── __init__.py
├── fraud-detection/          # Advanced fraud detection
│   ├── fraud_detector.py     # Multi-method fraud detection
│   └── __init__.py
├── main.py                  # MCP server entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- LandingAI Vision Agent API Key
- OpenAI API Key (optional, for enhanced Q&A)

### Installation
```bash
# Navigate to MCP server directory
cd mcp-server

# Install dependencies
pip install -r requirements.txt

# Install Pathway (for BDH architecture)
pip install -U pathway

# Set up environment variables
cp ../.env.example .env
# Edit .env with your API keys
```

### Configuration
1. **LandingAI Setup**: Get your API key from [LandingAI](https://landing.ai/)
2. **Environment Variables**: Configure `.env` file with your settings
3. **BDH Configuration**: Adjust neural network parameters in code

## 🚀 Quick Start

### Start the MCP Server
```bash
python main.py
```

### Test the API
```bash
# Health check
curl http://localhost:8000/health

# Analyze a document
curl -X POST "http://localhost:8000/analyze/document" \
     -H "Content-Type: application/json" \
     -d '{
       "document_path": "data/financial_docs/sample_contract.pdf",
       "analysis_type": "comprehensive",
       "use_bdh": true,
       "use_landingai": true
     }'

# Enhanced Q&A
curl -X POST "http://localhost:8000/qa/enhanced" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What are the payment terms?",
       "enhance_with_bdh": true
     }'

# Fraud detection
curl -X POST "http://localhost:8000/detect/fraud" \
     -H "Content-Type: application/json" \
     -d '{
       "document_text": "Payment shall be made within 30 days...",
       "document_type": "contract",
       "risk_threshold": 0.7
     }'
```

## 📊 API Endpoints

### Core Endpoints
- `GET /health` - System health check
- `POST /analyze/document` - Comprehensive document analysis
- `POST /qa/enhanced` - Enhanced Q&A with BDH
- `POST /detect/fraud` - Advanced fraud detection
- `POST /upload/document` - Document upload and processing

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔬 BDH Architecture Details

### Core Components
- **RoPE Integration**: Rotary position embeddings for better sequence understanding
- **Hebbian Learning**: Synaptic plasticity with excitatory/inhibitory circuits
- **Neuron Dynamics**: Sparse, positive activations with thresholding
- **Attention Patterns**: Interpretable attention mechanisms
- **Scalability**: Transformer-like scaling laws

### Financial Document Processing
- **Financial Term Recognition**: Specialized embeddings for financial terms
- **Legal Clause Analysis**: Neural classification of legal clauses
- **Risk Assessment**: Multi-factor risk scoring
- **Fraud Detection**: Neural network-based fraud probability

### Configuration
```python
config = BDHConfig(
    vocab_size=256,
    d_model=256,
    n_heads=4,
    n_neurons=32768,
    n_layers=6,
    dropout=0.05,
    integrate_with_pathway=True,
    enhance_qa_capabilities=True,
    fraud_detection_mode=True
)
```

## 🎯 Integration with Due Diligence Copilot

### Seamless Integration
The MCP server seamlessly integrates with the existing Due Diligence Copilot system:

- **Preserves existing functionality**: All original features remain intact
- **Enhances Q&A capabilities**: BDH-powered answer enhancement
- **Adds fraud detection**: Advanced fraud detection capabilities
- **Maintains audit logging**: Full compliance and audit trail
- **Extends API capabilities**: RESTful endpoints for external integration

### Enhanced Workflows
1. **Document Processing**: BDH-enhanced document analysis
2. **Q&A Enhancement**: Neural-powered answer improvement
3. **Fraud Detection**: Multi-method fraud assessment
4. **Risk Analysis**: Comprehensive risk scoring

## 📈 Performance & Scalability

### BDH Performance
- **Language Tasks**: Rivals GPT-2 performance at same parameter count
- **Document Analysis**: Sub-second processing for most documents
- **Memory Efficiency**: Optimized for GPU computation
- **Scalability**: Handles concurrent requests efficiently

### Integration Benefits
- **Enhanced Accuracy**: BDH improves analysis accuracy
- **Better Interpretability**: Neural insights for better understanding
- **Faster Processing**: Optimized neural processing
- **Scalable Architecture**: Production-ready deployment

## 🔒 Security & Compliance

### Security Features
- **API Authentication**: Secure API access
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Secure error responses
- **Audit Logging**: Complete activity logs

### Compliance
- **Data Privacy**: Local processing options
- **Regulatory Support**: Built-in compliance checks
- **Audit Trail**: Comprehensive audit logging
- **Encryption**: Secure data transmission

## 🧪 Testing & Development

### Running Tests
```bash
# Test BDH processor
python -c "from bdh_architecture import create_bdh_processor; create_bdh_processor()"

# Test fraud detection
python -c "from fraud_detection import create_fraud_detector; create_fraud_detector()"

# Test API endpoints
curl http://localhost:8000/health
```

### Development Setup
```bash
# Install development dependencies
pip install pytest black flake8 mypy

# Run linting
flake8 mcp-server/
black mcp-server/

# Type checking
mypy mcp-server/
```

## 📚 Usage Examples

### Document Analysis
```python
from mcp_server.bdh_architecture import analyze_document_with_bdh, create_bdh_processor

# Create BDH processor
processor = create_bdh_processor()

# Analyze document
analysis = analyze_document_with_bdh(
    processor, 
    "Payment shall be made within 30 days...", 
    "contract"
)

print(f"Risk Level: {analysis['risk_level']}")
print(f"Fraud Probability: {analysis['fraud_probability']:.3f}")
```

### Fraud Detection
```python
from mcp_server.fraud_detection import detect_fraud_in_document

# Detect fraud
fraud_results = detect_fraud_in_document(
    "Wire transfer to offshore account required...",
    transaction_data={"amount": 100000, "timestamp": "2024-01-01T02:00:00Z"}
)

print(f"Risk Level: {fraud_results['risk_level']}")
print(f"Recommendations: {fraud_results['recommendations']}")
```

### Enhanced Q&A
```python
from mcp_server.bdh_architecture import enhance_qa_with_bdh, create_bdh_processor

# Create processor
processor = create_bdh_processor()

# Enhance Q&A response
enhanced = enhance_qa_with_bdh(
    processor,
    "What are the payment terms?",
    "Payment shall be made within 30 days of invoice date.",
    "Contract payment terms section..."
)

print(f"Enhanced Answer: {enhanced['original_answer']}")
print(f"BDH Insights: {enhanced['bdh_insights']}")
```

## 🔮 Future Enhancements

### Planned Features
- **Multi-modal Analysis**: Image and text combined processing
- **Real-time Streaming**: Live document processing
- **Advanced ML Models**: Integration with additional AI models
- **Cloud Deployment**: Kubernetes and cloud-native deployment
- **Mobile SDK**: Mobile application integration

### Research Directions
- **Enhanced BDH**: Improved biological plausibility
- **Federated Learning**: Distributed model training
- **Quantum Integration**: Quantum-enhanced processing
- **Edge Computing**: Mobile and edge device support

## 🤝 Contributing

### Development Guidelines
1. Follow PEP 8 style guidelines
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Use type hints throughout

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **BDH Research**: Based on "The Dragon Hatchling" paper by Pathway researchers
- **LandingAI**: Advanced document extraction capabilities
- **Due Diligence Copilot**: Original system architecture
- **Open Source Community**: Various Python libraries and frameworks

## 📞 Support

- **Documentation**: Check the `/docs` endpoint for API documentation
- **Issues**: Report bugs and feature requests via GitHub issues
- **Discussions**: Join community discussions for questions and ideas

---

**Built for Hack with Bay - Financial Agents Challenge** 🚀

**Enhanced with BDH Architecture for the Future of AI-Powered Financial Analysis** 🧠