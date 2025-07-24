# ---------- Build Stage ----------
FROM python:3.11-slim AS builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    # Allow statements and log messages to immediately appear
    PYTHONUNBUFFERED=1 \
    # disable a pip version check to reduce run-time & log-spam
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # cache is useless in docker image, so disable to reduce image size
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential gcc libffi-dev python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files and source code
COPY setup.cfg pyproject.toml README.md download_models.py ./
COPY src ./src

# Build wheels
RUN pip wheel . --wheel-dir=/build/wheels

# Pre-install torch CPU (change version as needed)
RUN pip install torch>=2.7.1+cpu --index-url https://download.pytorch.org/whl/cpu

RUN pip install sentence-transformers>=5.0.0

RUN mkdir -p /build/hf_cache
RUN mkdir -p /build/hf_cache/hub

ENV HF_HOME=/build/hf_cache \
    HF_HUB_CACHE=/build/hf_cache/hub

# Download the model
RUN python download_models.py


# ---------- Final Stage ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/app/hf_cache \
    HF_HUB_CACHE=/app/hf_cache/hub

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create appuser
RUN groupadd -g 1000 appuser \
    && useradd -u 1000 -g appuser -s /bin/bash -m appuser

## Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools>=80.9.0 wheel

# Install built wheels and runtime deps
COPY --from=builder /build/wheels /tmp/wheels

RUN pip install --find-links=/tmp/wheels foi-search-service \
    && pip install uvicorn[standard] \
    && rm -rf /tmp/wheels

# Copy source code
COPY --from=builder /build/src ./src

COPY --from=builder /build/hf_cache /app/hf_cache

# Set ownership
RUN chown -R appuser:appuser /app
RUN chown -R appuser:appuser /app/hf_cache

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:80/health').read()" || exit 1

CMD ["python", "-m", "uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1"]
