set shell := ["powershell.exe", "-c"]


default:
    @just --list

# Format code using Black
format FILE = ".":
    uv tool run black {{FILE}}

format-check FILE = ".":
    uv tool run black {{FILE}} --diff

# Migrate the database
arevision MESSAGE:
    cd backend; uv run alembic revision --autogenerate -m "{{MESSAGE}}"

migrate TO = "head":
    cd backend; uv run alembic upgrade {{TO}}

# Run the development server
dev:
    cd backend; uv run uvicorn main:app --reload --log-level info

docker-run ENVIRONMENT="local":
    docker-compose -f docker-compose.{{ENVIRONMENT}}.yaml up --build -d

docker-down ENVIRONMENT="local":
    docker-compose -f docker-compose.{{ENVIRONMENT}}.yaml down
