# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements files
COPY requirements.txt /app/
COPY torch-requirements.txt /app/

# Install dependencies
RUN pip install -r torch-requirements.txt
RUN pip install -r requirements.txt

# Copy the entire application
COPY . /app/

# Copy the certificate into the container
COPY polybot/polybot-dev.crt /app/polybot/polybot-dev.crt

# Set the environment variable to ensure Python can find the modules
ENV PYTHONPATH=/app/polybot:$PYTHONPATH

# Define the default command to run your application
CMD ["python", "polybot/app.py"]
