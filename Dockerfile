FROM python:3.12-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY ./src .

ENV PATH="/app/.venv/bin:$PATH"
ENV UV_NO_DEV=1

RUN uv sync --locked

CMD ["uv", "run", "python3", "-m", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]