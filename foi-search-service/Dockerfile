FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/hf_cache \
    HF_HUB_CACHE=/hf_cache/hub

WORKDIR /app

# Only copy packaging & source (not tests/docs)
COPY setup.cfg pyproject.toml README.md ./
COPY src ./src

# Install build tools, then Python deps, then REMOVE build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl ca-certificates && \
    pip install --no-cache-dir --upgrade pip==24.0 && \
    pip install --no-cache-dir . && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Optionally, download models/caches (or let runtime do it and mount volume)
# COPY download_models.py .
# RUN python download_models.py && rm download_models.py

# Create non-root user and fix ownership
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1"]


