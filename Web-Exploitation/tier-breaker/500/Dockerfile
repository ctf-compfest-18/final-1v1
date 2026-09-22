FROM python:2.7-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=500.settings \
    DEBUG=1 \
    SECRET_KEY=4a654ccc12745bfb18fb23f4467fda63

WORKDIR /app

COPY src/requirements.txt ./requirements.txt

RUN python -m pip install --no-cache-dir "pip<21" "setuptools<45" \
    && pip install --no-cache-dir -r requirements.txt

COPY src/ ./

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080", "--noreload"]
