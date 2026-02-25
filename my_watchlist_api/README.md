# my_watchlist_api

Base FastAPI structure with SQLAlchemy + Pydantic and a simple User CRUD.

## Structure

- `app/main.py`: FastAPI app entrypoint
- `app/core/`: configuration
- `app/db/`: SQLAlchemy base and session
- `app/models/`: SQLAlchemy models
- `app/schemas/`: Pydantic schemas
- `app/repositories/`: data access layer (one file per repository)
- `app/api/v1/endpoints/`: API routes

## Run

```bash
cd my_watchlist_api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API base URL: `http://127.0.0.1:8000/api/v1`
