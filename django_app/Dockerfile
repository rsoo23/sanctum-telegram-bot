# django_app/Dockerfile
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
COPY start.sh /start.sh
RUN chmod +x start.sh

# Copy project
COPY /app /app
WORKDIR /app


# Run Django server
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
ENTRYPOINT [ "../start.sh" ]
