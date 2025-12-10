FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files first (better caching)
COPY pyproject.toml poetry.lock* ./

# Install dependencies without creating venv and without installing project root
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy entire project
COPY . .

# Run using python -m to avoid PATH issues
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
