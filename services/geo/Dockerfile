# syntax=docker/dockerfile:1
# API image only: the offline build (Earth Engine, pandas) is an optional extra and is not installed here.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS build
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim-bookworm
RUN useradd --system --uid 10001 geo
COPY --from=build --chown=geo /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PORT=8080
USER geo
EXPOSE 8080
ENTRYPOINT ["sh", "-c", "exec uvicorn shadowcast_geo.api:create_app --factory --host 0.0.0.0 --port ${PORT} --proxy-headers"]
