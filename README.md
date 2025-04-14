# FastAPI XTREM

A modern, secure FastAPI application with Streamlit frontend.

## Features

- FastAPI backend with OAuth2 authentication
- Streamlit frontend
- SQLAlchemy ORM with SQLite database
- JWT token-based authentication
- User management and roles
- Prometheus and Grafana monitoring
- Loguru for logging
- Docker support (coming soon)

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the API:
   ```bash
   cd api
   uvicorn main:app --reload
   ```

2. Start the Streamlit frontend:
   ```bash
   cd frontend
   streamlit run main.py
   ```

## API Documentation

Once running, visit:
- API docs: http://localhost:8000/docs
- Streamlit frontend: http://localhost:8501

## Project Structure

```
.
├── api/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── security.py
│   └── routes/
│       └── users.py
└── frontend/
    └── main.py