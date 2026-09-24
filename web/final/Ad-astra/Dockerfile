FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

LABEL org.opencontainers.image.title="ad-astra" \
      org.opencontainers.image.description="Bla"

WORKDIR /ad-astra

RUN useradd --create-home --uid 10001 adastra

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app.py .

USER adastra
EXPOSE 4007

CMD ["gunicorn", "--bind", "0.0.0.0:4007", "--workers", "2", "--threads", "4", \
     "--timeout", "15", "--graceful-timeout", "5", "--limit-request-line", "4096", \
     "--access-logfile", "-", "app:app"]
