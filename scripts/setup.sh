#!/bin/bash

echo "🚀 Setting up AI Agent Platform..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys!"
    echo ""
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p backend/data/uploads
mkdir -p backend/data/chroma

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
echo ""

# Check PostgreSQL
echo -n "PostgreSQL: "
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Ready"
else
    echo "❌ Not ready"
fi

# Check ChromaDB
echo -n "ChromaDB: "
if curl -s http://localhost:8001/api/v1/heartbeat > /dev/null 2>&1; then
    echo "✅ Ready"
else
    echo "⚠️  Starting (may take a moment)"
fi

# Check Backend
echo -n "Backend API: "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Ready"
else
    echo "⚠️  Starting (may take a moment)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Restart services: docker-compose restart backend"
echo "3. Access API docs: http://localhost:8000/docs"
echo "4. Run examples: cd examples && python agent_example.py"
echo ""
echo "📖 For more information, see README_PLATFORM.md"
