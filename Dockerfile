FROM python:3.13-slim

ARG APP_DIR=/source
WORKDIR ${APP_DIR}

ENV PATH=${APP_DIR}/.venv/bin:${PATH} \
	PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install gettext (for compiling messages to other languages) and uv (single static binary) and clean up
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh \
    && apt-get purge -y curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy source code
COPY source/ ./source/
COPY alembic.ini ./alembic.ini
COPY alembic/ ./alembic/

# Expose port (Railway will set PORT environment variable)
EXPOSE 8000

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/status || exit 1
