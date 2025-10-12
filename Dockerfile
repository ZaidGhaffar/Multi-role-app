FROM python:3.13-alpine
COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/

RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev && \
    apk add postgresql-dev

WORKDIR /app

COPY . /app/

RUN pip install uv
RUN uv sync --locked

EXPOSE 8080

CMD ["uv", "run", "main.py"]

