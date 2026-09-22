FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Place the password-protected participant distribution ZIP in public/ before building.
COPY --chmod=444 public/challenge.zip ./

USER 10001:10001

EXPOSE 3000

CMD ["python", "-m", "http.server", "3000", "--bind", "0.0.0.0", "--directory", "/app"]
