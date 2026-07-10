FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "infrastructure.entrypoints.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
