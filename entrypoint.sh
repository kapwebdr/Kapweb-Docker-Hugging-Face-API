#!/bin/sh
pip install --no-cache-dir -r /app/requirements.txt
exec "$@"