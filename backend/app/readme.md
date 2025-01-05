# Mental Health API

This document provides instructions on how to set up and run the Mental Health API application.

## Prerequisites

- Docker and Docker Compose
- Poetry (Python package manager)
- Python 3.8+

## Setup Instructions

1. **Environment Configuration**
   ```bash
   # Copy the environment template file
   cp .env.template .env
   
   # Edit .env file and add your secrets
   # Make sure to update:
   # - DATABASE_URL
   # - OPENAI_API_KEY
   # - Other required secrets
   ```

2. **Start Docker Services**
   ```bash
   # Start all required services (Redis, PostgreSQL, etc.)
   docker-compose up -d
   ```

3. **Run FastAPI Application**
   ```bash
   # Install dependencies
   poetry install

   # Start the FastAPI server
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start Celery Worker**
   ```bash
   # In a new terminal, start the Celery worker
   poetry run celery -A app.worker worker --loglevel=info
   ```

5. **Start Flower Dashboard (Optional)**
   ```bash
   # In a new terminal, start the Flower monitoring UI
   poetry run celery -A app.worker flower --port=5555
   ```

## Accessing the Services

- FastAPI Application: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Flower Dashboard: http://localhost:5555

## Development

The API includes CORS middleware configured for the following origins:
- http://localhost:3000 (React dev server)
- http://localhost:5173 (Vite dev server)

## Troubleshooting

If you encounter any issues:
1. Ensure all required services are running (`docker-compose ps`)
2. Check the logs (`docker-compose logs`)
3. Verify your environment variables are properly set
4. Ensure all ports are available and not in use by other services
