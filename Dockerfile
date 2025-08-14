# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Set environment variable placeholder (will be overridden in Render)
ENV BOT_TOKEN=""

# Run bot
CMD ["python", "bot.py"]
