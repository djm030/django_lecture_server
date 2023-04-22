FROM python:3.11-slim as builder

WORKDIR /app

# Installing OS packages and tools
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    default-libmysqlclient-dev

# Install Poetry
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir "poetry>=1.1.8"

# Copy pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock ./

# Update Poetry lock file
RUN poetry lock --no-update

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main --extras "mysql"

# Copy project files
COPY . /app

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "config.wsgi:application", "--daemon", "--bind", "0.0.0.0:8000", "--access-logfile", "access.log", "--error-logfile", "error.log"]