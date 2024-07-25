# bot/Dockerfile
FROM python:3.10-slim

# Set environment variables
# not to generate pyc (for smaller size in container)
ENV PYTHONDONTWRITEBYTECODE 1
# disable output buffering
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Copy project
COPY /app /app
WORKDIR /app

# Copy assets
COPY /assets /assets

# Run Telegram bot
CMD ["watchmedo", "auto-restart", "--directory=./", "--pattern=*.py", "--recursive", "--", "python3", "bot.py"]
