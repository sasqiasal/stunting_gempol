FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for psycopg2 etc
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
# We copy index.py and the app directory into /app
COPY index.py .
COPY app ./app

# Expose port (standard FastAPI port)
EXPOSE 8000

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
