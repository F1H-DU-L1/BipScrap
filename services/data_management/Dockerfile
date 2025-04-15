# Use a lightweight Python image
FROM python:3.11-slim

# Set environment variables so Flask runs correctly
ENV FLASK_APP=api
ENV FLASK_RUN_HOST=0.0.0.0

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . .

# Expose the port on which Flask will run
EXPOSE 5000

# Default command to run the application
CMD ["flask", "run"]
