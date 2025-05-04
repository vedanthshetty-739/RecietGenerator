# Use an official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

EXPOSE 8000

# Install system dependencies for weasyprint
# Install wkhtmltopdf dependencies
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


ENV XDG_RUNTIME_DIR=/tmp


# Copy app code
COPY ./src .

# Fix file permissions *after* copying static assets
RUN chmod -R 755 static

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
