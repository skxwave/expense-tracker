# 💰 Expense Tracker API

A lightweight FastAPI-based REST API for tracking personal expenses and income with JWT authentication.

## Features

- **Transaction Tracking** - Log expenses and income with descriptions and timestamps
- **Financial Summary** - Get total expenses and income at a glance
- **Goals tracking** - Creating goals

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLAlchemy ORM with async support
- **Migrations:** Alembic
- **Authentication:** JWT with AuthX
- **Validation:** Pydantic

## Getting Started

### Prerequisites

- Python 3.14+
- PostgreSQL or SQLite

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd expense_tracker
```

2. Install dependencies:
```bash
uv sync
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the server:
```bash
# Using justfile:
just dev

# Or manually:
cd backend
uv run uvicorn main:app --reload --log-level info
```

The API will be available at `http://localhost:8000`

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Status

🚀 Early-stage development - Core features functional, more to come!

## License

MIT
