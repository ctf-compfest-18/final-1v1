FROM python:3.13-slim

WORKDIR /app
COPY src/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./
RUN useradd -r -u 10001 appuser && chown -R appuser:appuser /app
USER appuser
ENV FLAG = "COMPFEST18{8be3c5825e5e572ab0bfd34c2673763343d789fc387c7ae71cc82161db9dd556}"
EXPOSE 8080
CMD ["python", "app.py"]
