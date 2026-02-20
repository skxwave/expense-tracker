FROM python:3.14.2-slim AS final

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Install uv
RUN pip install uv

# Copy only the dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies with `uv` without copying the whole app yet
RUN uv sync --frozen --no-install-project --no-dev

# Now copy the rest of the app
COPY . .

# Sync the project itself
RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
