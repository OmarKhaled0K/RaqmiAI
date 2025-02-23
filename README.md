# RaqmiAI Voice Chat System

Internal voice chat system for Raqmi AI, providing voice-to-voice conversational AI capabilities with RAG support.

## Overview

This system handles:
- Voice transcription from audio files
- Context retrieval from our knowledge base
- LLM-powered response generation
- Text-to-speech conversion
- Audio streaming delivery

## Development Setup

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- AWS credentials (stored in SSM)
- Access to company VPN for vector database connection

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/OmarKhaled0K/RaqmiAI.git
   cd RaqmiAI
   ```

2. **Environment Setup**
   ```bash
   # Copy the template env file
   cp .env.example .env
   
   # Get the required secrets from AWS SSM
   # Contact Omar (omarkhaledcvexpert@gmail.com) for access
   ```

3. **Running the Application**

   Development mode with hot reload:
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

   Production simulation:
   ```bash
   docker-compose up --build
   ```

## Project Structure

```
src/
├── api/                 # FastAPI routes & middleware
├── core/               # Core configuration
├── services/           # Business logic
├── adapters/           # External service integrations
└── utils/             # Shared utilities
```

### Key Components:

- `services/audio/`: Speech processing pipeline
- `services/llm/`: LLM integration interfaces
- `services/vector_store/`: RAG implementation
- `adapters/`: Cloud provider integrations

## Development Guidelines

1. **Branch Naming**
   - Feature: `feature/description`
   - Bug: `fix/description`
   - Release: `release/v1.x.x`

2. **Code Standards**
   - Use type hints
   - Write docstrings for public functions
   - Keep functions focused and small
   - Add tests for new features

3. **Testing**
   ```bash
   # Run tests locally
   pytest

   # Run with coverage
   pytest --cov=src tests/
   ```

4. **Adding New Cloud Providers**
   1. Create new adapter in `src/adapters/`
   2. Implement required base classes
   3. Update configuration
   4. Add tests
   5. Update deployment scripts

## Deployment

Currently deployed on AWS ECS. Deployment is handled through our CI/CD pipeline on push to main.

### Infrastructure
- ECS for container orchestration
- S3 for audio storage
- ElastiCache for response caching
- AWS Transcribe/Polly for speech services

### Monitoring
- CloudWatch for logs and metrics
- Prometheus for custom metrics
- Grafana dashboards (links in internal wiki)

## Troubleshooting

Common issues and solutions:

1. **Vector DB Connection**
   - Check VPN connection
   - Verify credentials in `.env`
   - Ensure correct environment selected

2. **AWS Services**
   - Verify AWS credentials
   - Check service quotas
   - Review CloudWatch logs

## Team Contacts

- **Project Lead**: [Omar Khaled](omarkhaledcvexpert@gmail.com)
- **DevOps Support**: [Name](email)
- **AWS Account Access**: [Name](email)

## Documentation

- Internal API docs: [Link to internal Swagger]
- Architecture diagrams: [Link to internal wiki]
- Deployment guide: [Link to internal wiki]

---

## To start the project:

1. Set up your virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate  # Windows
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Start the development server:
```bash
uvicorn main:app --reload
```

