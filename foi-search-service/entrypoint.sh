#!/bin/bash
# Fix permissions before starting the app
chown -R appuser:appuser /app/hf_cache
exec "$@"