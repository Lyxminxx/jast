FROM python:3.14-slim

# Install uv directly into the container
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Copy your project files
COPY . .

# Tell uv to sync dependencies (this creates a clean .venv inside the container)
RUN uv sync --no-dev

# Collect static files for the admin panel using uv run
RUN uv run python manage.py collectstatic --noinput

# Create the data directory for SQLite
RUN mkdir -p data

# Expose the port
EXPOSE 8000

# Start Gunicorn using uv run
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
