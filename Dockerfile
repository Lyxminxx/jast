FROM python:3.14-slim

# Install uv directly into the container
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Copy your project files
COPY . .

# Tell uv to sync/install all dependencies into the system environment
RUN uv sync --system --no-dev

# Collect static files for the admin panel
RUN python manage.py collectstatic --noinput

# Create the data directory for SQLite
RUN mkdir -p data

# Expose the port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
