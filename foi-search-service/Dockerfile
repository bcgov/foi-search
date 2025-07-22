# ---------- Build Stage ----------
FROM python:3.11-slim-bullseye AS builder

WORKDIR /build

# Install build dependencies only in the build stage
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only what is needed to install dependencies
COPY setup.cfg pyproject.toml README.md ./
COPY src ./src

# Install Python dependencies to a wheelhouse (or into /build/venv)
RUN pip install --upgrade pip==24.0 \
 && pip wheel . --wheel-dir=/build/wheels

# ---------- Final (Runtime) Stage ----------
FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/hf_cache \
    HF_HUB_CACHE=/hf_cache/hub

WORKDIR /app

# Copy only built dependencies (wheels) and install
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir --find-links=/wheels your-package-name

# Copy source code (no build tools!)
COPY src ./src
COPY setup.cfg pyproject.toml README.md ./

# Create user (optional)
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1"]
