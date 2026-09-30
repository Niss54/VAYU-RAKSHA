# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS build
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
COPY services/geo/pyproject.toml services/geo/uv.lock services/geo/README.md ./
RUN uv sync --no-dev --no-install-project
COPY services/geo/src ./src
RUN uv sync --no-dev --no-editable

FROM python:3.12-slim-bookworm
WORKDIR /app
RUN useradd --system --uid 10001 geo && mkdir -p /app && chown -R geo:geo /app
COPY --from=build --chown=geo /app/.venv /app/.venv
COPY --from=build --chown=geo /app/src /app/src
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH="/app/src:$PYTHONPATH" PYTHONUNBUFFERED=1 PORT=8080
USER geo
EXPOSE 8080
ENTRYPOINT ["sh", "-c", "exec uvicorn shadowcast_geo.api:create_app --factory --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers"]
