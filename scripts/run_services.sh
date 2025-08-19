# app/entrypoint.sh
#!/usr/bin/env bash

set -e

# chech ENABLE_MIGRATION environment variable
if [ "$ENABLE_MIGRATION" = "true" ]; then
    echo "Running Alembic migrations..."
    alembic upgrade head
fi

echo "Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000