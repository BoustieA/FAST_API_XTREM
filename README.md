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
## Linter

```bash
# Installation des outils
pip install black isort flake8 pylint

# Formatage avec Black
black fast_api_xtrem

# Organisation des imports
isort fast_api_xtrem

# Vérification Flake8
flake8 fast_api_xtrem

# Vérification Pylint (optionnel mais utile)
pylint fast_api_xtrem
```

## Running the Application

1. Start the API:
   ```bash
   python -m fast_api_xtrem.main
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
