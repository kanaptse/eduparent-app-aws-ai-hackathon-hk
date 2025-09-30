#!/bin/bash

echo "🚀 Setting up EduParent development environment..."

# Create scripts directory if it doesn't exist
mkdir -p scripts

# Backend setup
echo "📦 Setting up backend..."
cd apps/backend
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    pip install uv
fi
uv sync
cd ../..

# Frontend setup  
echo "📱 Setting up frontend..."
cd apps/frontend
flutter pub get
cd ../..

# Copy environment files
echo "⚙️  Setting up environment files..."
if [ ! -f apps/backend/.env ]; then
    cp apps/backend/.env.example apps/backend/.env
    echo "Created apps/backend/.env"
fi

if [ ! -f infra/.env ]; then
    cp infra/.env.example infra/.env
    echo "Created infra/.env"
fi

echo "✅ Setup complete!"
echo ""
echo "To start development:"
echo "  Backend: cd apps/backend && uv run uvicorn app.main:app --reload"
echo "  Frontend: cd apps/frontend && flutter run"
echo "  Full stack: cd infra && docker-compose up"