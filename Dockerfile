# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port your app will run on
EXPOSE 8080

# Run the Flask app with Waitress
CMD ["python", "-m", "waitress", "--host=0.0.0.0", "--port=8080", "--threads=4", "RoundSimulationApi:app"]
