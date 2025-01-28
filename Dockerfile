# Using the official Python image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Set up a working directoryCopy only dependency files before installation to cache Docker layers
COPY requirements.txt .

# Installing dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Then  copy the remaining files
COPY . .

# Opening a port for a web application
EXPOSE 8000

# Launching the application
CMD ["python", "app.py"]
