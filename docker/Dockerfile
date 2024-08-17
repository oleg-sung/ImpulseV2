# Pull the official base image
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/molniya/src"

# Create and set work directory
WORKDIR /molniya

# Upgrade pip and install dependencies
COPY /requirements/requirements.dev.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.dev.txt

# Copy application source code
COPY /src ./src
COPY /env ./env
