FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data /app/chroma_db

# Expose the port your app runs on
EXPOSE 8000

# Use uvicorn to run the FastAPI application
CMD ["uvicorn", "service.api:app", "--host", "0.0.0.0", "--port", "8000"]