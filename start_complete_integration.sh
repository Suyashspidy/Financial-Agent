#!/bin/bash

# Financial Agent Complete Integration Startup Script
# Starts all components: Frontend, Enhanced Claims API, LandingAI MCP Server, and Inkeep

echo "🚀 Starting Financial Agent Complete Integration"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${RED}❌ Port $1 is already in use${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Port $1 is available${NC}"
        return 0
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $service_name to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready!${NC}"
            return 0
        fi
        echo -e "${YELLOW}   Attempt $attempt/$max_attempts - waiting...${NC}"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service_name failed to start within timeout${NC}"
    return 1
}

# Check required ports
echo -e "${BLUE}🔍 Checking port availability...${NC}"
check_port 5173 || exit 1  # Frontend
check_port 8000 || exit 1  # Enhanced Claims API
check_port 8001 || exit 1  # LandingAI MCP Server
check_port 3000 || exit 1  # Inkeep UI
check_port 3002 || exit 1  # Inkeep Manage API
check_port 3003 || exit 1  # Inkeep Run API

# Create uploads directory
mkdir -p uploads
echo -e "${GREEN}✅ Created uploads directory${NC}"

# Start LandingAI MCP Server
echo -e "${BLUE}🤖 Starting LandingAI MCP Server...${NC}"
cd /home/abhin/Financial-Agent-mcp/agent_dir
source ../venv/bin/activate
python financial_mcp_server.py &
LANDINGAI_PID=$!
echo -e "${GREEN}✅ LandingAI MCP Server started (PID: $LANDINGAI_PID)${NC}"

# Wait for LandingAI MCP Server
wait_for_service "http://localhost:8001/health" "LandingAI MCP Server" || exit 1

# Start Enhanced Claims API
echo -e "${BLUE}🔧 Starting Enhanced Claims API...${NC}"
cd /home/abhin/Financial-Agent-mcp
source venv/bin/activate
python enhanced_claims_api.py &
CLAIMS_API_PID=$!
echo -e "${GREEN}✅ Enhanced Claims API started (PID: $CLAIMS_API_PID)${NC}"

# Wait for Enhanced Claims API
wait_for_service "http://localhost:8000/health" "Enhanced Claims API" || exit 1

# Start Frontend
echo -e "${BLUE}🌐 Starting Frontend...${NC}"
cd /home/abhin/Financial-Agent-mcp/frontend
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for Frontend
wait_for_service "http://localhost:5173" "Frontend" || exit 1

# Start Inkeep Agent System
echo -e "${BLUE}🧠 Starting Inkeep Agent System...${NC}"
cd /home/abhin/Financial-Agent-mcp/agent_dir
npm run dev &
INKEEP_PID=$!
echo -e "${GREEN}✅ Inkeep Agent System started (PID: $INKEEP_PID)${NC}"

# Wait for Inkeep
wait_for_service "http://localhost:3000" "Inkeep UI" || exit 1

echo ""
echo -e "${GREEN}🎉 ALL SERVICES STARTED SUCCESSFULLY!${NC}"
echo "================================================"
echo ""
echo -e "${BLUE}🌐 Access Points:${NC}"
echo -e "   Frontend:           ${GREEN}http://localhost:5173${NC}"
echo -e "   Enhanced Claims API: ${GREEN}http://localhost:8000${NC}"
echo -e "   LandingAI MCP:       ${GREEN}http://localhost:8001${NC}"
echo -e "   Inkeep UI:           ${GREEN}http://localhost:3000${NC}"
echo -e "   Inkeep Manage API:   ${GREEN}http://localhost:3002${NC}"
echo -e "   Inkeep Run API:      ${GREEN}http://localhost:3003${NC}"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo -e "   Enhanced API Docs:   ${GREEN}http://localhost:8000/docs${NC}"
echo -e "   LandingAI API Docs:  ${GREEN}http://localhost:8001/docs${NC}"
echo ""
echo -e "${YELLOW}🧪 To run integration tests:${NC}"
echo -e "   cd /home/abhin/Financial-Agent-mcp"
echo -e "   source venv/bin/activate"
echo -e "   python test_complete_integration.py"
echo ""
echo -e "${YELLOW}🛑 To stop all services:${NC}"
echo -e "   kill $LANDINGAI_PID $CLAIMS_API_PID $FRONTEND_PID $INKEEP_PID"
echo ""

# Open frontend in browser
echo -e "${BLUE}🌐 Opening frontend in browser...${NC}"
xdg-open http://localhost:5173 2>/dev/null || echo -e "${YELLOW}⚠️  Could not open browser automatically${NC}"

# Keep script running and show status
echo -e "${BLUE}📊 Service Status Monitor (Press Ctrl+C to stop all services)${NC}"
echo "================================================"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping all services...${NC}"
    kill $LANDINGAI_PID $CLAIMS_API_PID $FRONTEND_PID $INKEEP_PID 2>/dev/null
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Monitor services
while true; do
    echo -e "${BLUE}$(date '+%H:%M:%S') - Services running...${NC}"
    sleep 30
done
