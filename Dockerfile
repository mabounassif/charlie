# Use a base image with Stockfish pre-installed
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies including Stockfish
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    stockfish \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port for potential web interface (if added later)
EXPOSE 8000

# Set the default command to run the web application for Railway
CMD ["python3", "run_api.py"] 