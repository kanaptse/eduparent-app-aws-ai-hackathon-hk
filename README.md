# EduParent App

A cross-platform parenting communication app that helps parents develop effective communication skills with their children through evidence-based content, AI-powered roleplay practice, and daily action challenge.

## What is EduParent?

EduParent provides parents with:
- **Daily communication feed** with evidence-based parenting techniques
- **AI roleplay practice** to safely practice difficult conversations with virtual child characters
- **Daily action challenges** to apply learned skills in real-world situations 

Built with Flutter (cross-platform mobile/web) and Python FastAPI backend.

## Project Structure

```
eduparent-app/
├── apps/
│   ├── frontend/          # Flutter app (iOS/Android/Web)
│   └── backend/           # FastAPI backend + SQLite database
├── packages/              # Shared code (future use)
├── infra/                 # Docker development environment
└── scripts/               # Setup and utility scripts
```

## Quick Start

### Prerequisites
- Flutter SDK (latest stable)
- Python 3.11+ with uv package manager
- Docker & Docker Compose (optional)

### 1. Backend Setup
```bash
cd apps/backend

# Copy environment file and configure
cp .env.example .env
# Edit .env with your API keys:
# OPENAI_API_KEY=your_openai_key_here
# EVALUATION_MODEL=openai:gpt-4o-mini
# TEEN_RESPONSE_MODEL=openai:gpt-4o-mini

# Install dependencies and run
pip install uv
uv sync
uv run uvicorn app.main:app --reload
```
Backend runs at http://localhost:8000

### 2. Frontend Setup
```bash
cd apps/frontend
flutter pub get
flutter run
```
Choose your target platform when prompted (iOS/Android/Web/macOS).

### 3. Docker Development (Alternative)
```bash
cd infra
cp ../apps/backend/.env.example ../apps/backend/.env
# Edit ../apps/backend/.env with your API keys
docker-compose up --build
```
- Backend: http://localhost:8000
- Database Admin: http://localhost:8080
- PostgreSQL: localhost:5432

## Environment Configuration

Copy `apps/backend/.env.example` to `apps/backend/.env` and configure:

```bash
# Model Configuration
# openai:gpt-4o-mini or bedrock:deepseek.v3-v1:0
EVALUATION_MODEL=openai:gpt-4o-mini
TEEN_RESPONSE_MODEL=openai:gpt-4o-mini

# API Keys
OPENAI_API_KEY=your_openai_key_here
AWS_ACCESS_KEY_ID=your_aws_key_here  # Optional for AWS Bedrock
AWS_SECRET_ACCESS_KEY=your_aws_secret_here
AWS_REGION=us-east-1

# Game Configuration
MAX_ATTEMPTS=3
PASS_THRESHOLD=7
SCENARIOS_DIR=app/roleplay/scenarios/data
```

## Development Commands

### Backend
```bash
cd apps/backend
uv run uvicorn app.main:app --reload    # Start dev server
uv run ruff check .                     # Lint code
uv run pytest                           # Run tests
```

### Frontend
```bash
cd apps/frontend
flutter run                             # Start app
flutter run -d chrome                   # Run on web
flutter analyze                         # Lint code
flutter test                            # Run tests
```

## Tech Stack

- **Frontend**: Flutter (Dart) - iOS, Android, Web, macOS
- **Backend**: FastAPI (Python) with Pydantic validation
- **Database**: SQLite (development) → PostgreSQL (production)
- **AI**: OpenAI GPT models or AWS Bedrock
- **Infrastructure**: Docker, Docker Compose

## Current Features

- ✅ User registration and basic authentication
- ✅ Daily communication feed with parenting content
- ✅ Parent-child communication assessment surveys
- ✅ AI-powered roleplay scenarios with virtual teenagers
- ✅ Progress tracking and evaluation system

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

