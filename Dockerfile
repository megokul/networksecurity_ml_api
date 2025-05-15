FROM python:3.10-slim-buster

# Set working directory inside container
WORKDIR /app

# Copy everything from host to container's /app directory
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
