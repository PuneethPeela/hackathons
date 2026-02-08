#!/bin/bash

# AI Patient Support Assistant - Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up AI Patient Support Assistant..."

# Colors for output
GREEN='\033[0.32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11+${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python found${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker is not installed. Please install Docker to use containerized services${NC}"
else
    echo -e "${GREEN}✓ Docker found${NC}"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose is not installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose found${NC}"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
cd backend
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit backend/.env with your configuration${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Start Docker services
if command -v docker-compose &> /dev/null; then
    echo "🐳 Starting Docker services..."
    cd ..
    docker-compose up -d postgres mongodb redis
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    cd backend
    
    # Run migrations
    echo "🗄️  Running database migrations..."
    python migrations/run_migrations.py
    
    # Initialize MongoDB
    echo "🍃 Initializing MongoDB..."
    python -m app.mongodb.init_collections
    python -m app.mongodb.seed_data
    
    echo -e "${GREEN}✅ Setup complete!${NC}"
    echo ""
    echo "To start the application:"
    echo "  1. Activate virtual environment: source backend/venv/bin/activate"
    echo "  2. Run the server: python backend/run.py"
    echo ""
    echo "The API will be available at http://localhost:5000"
else
    echo -e "${YELLOW}⚠️  Docker Compose not found. Please start PostgreSQL, MongoDB, and Redis manually${NC}"
    echo -e "${YELLOW}   Then run:${NC}"
    echo "     python migrations/run_migrations.py"
    echo "     python -m app.mongodb.init_collections"
    echo "     python -m app.mongodb.seed_data"
fi

echo ""
echo "📚 Documentation:"
echo "  - README.md - Project overview"
echo "  - DEPLOYMENT.md - Deployment guide"
echo "  - CONTRIBUTING.md - Contributing guidelines"
echo ""
echo "🧪 To run tests:"
echo "  pytest"
echo "  pytest --cov=app"
echo ""
echo -e "${GREEN}Happy coding! 🎉${NC}"
