# Use an official lightweight Python runtime
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies without storing cache to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the default Cloud Run port
EXPOSE 8080

# Run the FastAPI application
# Ensure your main Python file is named main.py and inside a src/ folder
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]