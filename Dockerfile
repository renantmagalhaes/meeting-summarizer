# Step 1: Use an official Python runtime as a parent image
# Using a 'slim' version for a smaller image size
FROM python:3.11-slim

# Step 2: Install system dependencies required by the app
# - ffmpeg is crucial for Whisper to process audio
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg git && rm -rf /var/lib/apt/lists/*

# Step 3: Set the working directory in the container
WORKDIR /app

# Step 4: Copy and install Python requirements
# This is done in a separate step to leverage Docker's layer caching.
# The layer will only be rebuilt if requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the application code into the container
COPY . .

# Step 6: Expose the port the app runs on (documentation purpose)
# The actual port mapping is done in docker-compose.yml
EXPOSE 5001

# Step 7: Define the command to run the application
CMD ["python", "app.py"]