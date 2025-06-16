# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the entire application
COPY . .

RUN pip install -r ./polybot/requirements.txt

# Define the default command to run your application
CMD ["python", "-m", "polybot.app"]
