FROM python:3.10-slim-buster

WORKDIR /app

# Copy only requirements and setup.py files first (for dependency install layer)
COPY requirements.txt setup.py ./

# make sure your actual package is inside `src/`
COPY src ./src  

# Install dependencies (editable mode works now because code is present)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code (non-package files, e.g., app.py, tests)
COPY . .

# Start FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
