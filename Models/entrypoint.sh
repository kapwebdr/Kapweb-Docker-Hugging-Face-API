#!/bin/sh
pip install --no-cache-dir -r /app/requirements.txt
export TRANSFORMERS_CACHE=/app/cache/
exec "$@"