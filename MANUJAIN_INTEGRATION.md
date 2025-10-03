# Financial Agent - Manujain Branch Integration

## 🚀 Complete Integration Overview

This is the **manujain branch** integration of the Financial Agent system, featuring a comprehensive FastAPI backend with LandingAI MCP server integration, React frontend, and Inkeep agent management system.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  Enhanced Claims│    │ LandingAI MCP   │
│   (Port 5173)    │◄──►│      API       │◄──►│    Server       │
│                 │    │   (Port 8000)   │    │   (Port 8001)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Inkeep Agent   │
                       │   Management    │
                       │   (Port 3000)   │
                       └─────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
            ┌─────────────┐         ┌─────────────┐
            │ Manage API  │         │  Run API    │
            │ (Port 3002) │         │(Port 3003)  │
            └─────────────┘         └─────────────┘
```

## 🔧 Components

### 1. Enhanced Claims API (`enhanced_claims_api.py`)
- **Port**: 8000
- **Features**:
  - PDF document upload and processing
  - AI-powered claim analysis
  - Team assignment and reassignment
  - Question answering system
  - Integration with LandingAI MCP server
  - Real-time status updates

### 2. LandingAI MCP Server (`financial_mcp_server.py`)
- **Port**: 8001
- **Features**:
  - Document processing and analysis
  - Question answering capabilities
  - Risk assessment and scoring
  - Data extraction and citation
  - Realistic AI simulation

### 3. React Frontend (`frontend/`)
- **Port**: 5173
- **Features**:
  - Drag & drop PDF upload
  - Real-time dashboard
  - Claim management interface
  - Team reassignment functionality
  - Responsive design

### 4. Inkeep Agent System (`agent_dir/`)
- **Ports**: 3000 (UI), 2001 (Manage UI), 3002 (Manage API), 3003 (Run API)
- **Features**:
  - Agent management interface
  - MCP server integration
  - Workflow orchestration
  - Real-time monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm/pnpm

### Installation & Startup

1. **Clone and checkout manujain branch**:
   ```bash
   git checkout manujain
   ```

2. **Run the complete integration script**:
   ```bash
   ./start_manujain_integration.sh
   ```

   This script will:
   - Install all dependencies
   - Start all services
   - Verify health checks
   - Open the frontend in your browser

### Manual Startup (Alternative)

1. **Install Python dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Start LandingAI MCP Server**:
   ```bash
   cd agent_dir
   source ../venv/bin/activate
   python financial_mcp_server.py
   ```

3. **Start Enhanced Claims API**:
   ```bash
   cd ..
   source venv/bin/activate
   python enhanced_claims_api.py
   ```

4. **Start Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Start Inkeep Agent System**:
   ```bash
   cd ../agent_dir
   npm install
   npm run dev
   ```

## 🧪 Testing

Run the comprehensive integration test:

```bash
source venv/bin/activate
python test_manujain_integration.py
```

This will test:
- ✅ Service health checks
- ✅ Document upload functionality
- ✅ AI-powered claim analysis
- ✅ Question answering system
- ✅ Claim reassignment
- ✅ LandingAI MCP integration

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | React application |
| **Enhanced Claims API** | http://localhost:8000 | FastAPI backend |
| **LandingAI MCP Server** | http://localhost:8001 | Document processing |
| **Inkeep UI** | http://localhost:3000 | Agent management |
| **Manage UI** | http://localhost:2001 | Next.js management |
| **Manage API** | http://localhost:3002 | Inkeep management API |
| **Run API** | http://localhost:3003 | Inkeep execution API |

## 📚 API Documentation

- **Enhanced Claims API**: http://localhost:8000/docs
- **LandingAI MCP Server**: http://localhost:8001/docs

## 🔗 Key Features

### Document Processing
- PDF upload with validation
- Background processing
- Real-time status updates
- File storage management

### AI Analysis
- Severity scoring (1-10)
- Complexity assessment
- Team assignment suggestions
- Risk flag identification
- Confidence scoring

### Question Answering
- Document-based Q&A
- Context-aware responses
- Citation tracking
- Evidence extraction

### Team Management
- Automatic team assignment
- Manual reassignment
- Team performance tracking
- Workflow optimization

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
LANDINGAI_MCP_SERVER_URL=http://localhost:8001
UPLOAD_DIR=uploads
LOG_LEVEL=INFO
```

### Port Configuration
All ports are configurable in the respective service files:
- Enhanced Claims API: `enhanced_claims_api.py` (line 380)
- LandingAI MCP Server: `financial_mcp_server.py` (line 380)
- Frontend: `frontend/vite.config.js`
- Inkeep: `agent_dir/package.json`

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**:
   ```bash
   # Kill processes on specific ports
   kill -9 $(lsof -t -i:8000)
   kill -9 $(lsof -t -i:8001)
   kill -9 $(lsof -t -i:5173)
   ```

2. **Dependencies not installed**:
   ```bash
   # Reinstall Python dependencies
   pip install -r requirements.txt
   
   # Reinstall Node dependencies
   cd frontend && npm install
   cd ../agent_dir && npm install
   ```

3. **Services not starting**:
   - Check logs for specific error messages
   - Verify all required ports are available
   - Ensure Python virtual environment is activated

### Logs
- Enhanced Claims API: Console output
- LandingAI MCP Server: Console output
- Frontend: Browser console + terminal
- Inkeep: Terminal output

## 📈 Performance

### Expected Performance
- Document upload: < 2 seconds
- AI analysis: 2-5 seconds
- Question answering: 1-3 seconds
- Page load: < 1 second

### Optimization Tips
- Use SSD storage for uploads directory
- Ensure adequate RAM (8GB+ recommended)
- Close unnecessary applications
- Use Chrome/Firefox for best frontend performance

## 🔒 Security

### Current Security Features
- CORS configuration
- File type validation
- Input sanitization
- Error handling

### Production Considerations
- Add authentication/authorization
- Implement rate limiting
- Use HTTPS
- Add input validation
- Implement logging and monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the Financial Agent system. Please refer to the main repository for licensing information.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Run the integration test
4. Create an issue in the repository

---

**🎉 The manujain branch integration is ready for use!**
