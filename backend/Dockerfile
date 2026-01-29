# Use Python 3.9 as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Expect frontend/dist to be copied into a specific path
# We will copy it from the host during build
COPY ./frontend_dist ./frontend_dist

# Set environment variables
ENV FRONTEND_PATH=/app/frontend_dist
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Start command
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
