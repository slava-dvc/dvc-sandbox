#!/bin/bash
set -e


# Read PORT from environment variable or set default to 8080 if not provided
PORT=${PORT:-8080}
# Store the first argument
command="$1"
# Shift once to remove the first argument
shift

if [ "$command" = 'backend' ]; then
    exec python -m app.backend "$@"
elif [ "$command" = 'job' ]; then
    exec python -m app.job "$@"
elif [ "$command" = "portfolio" ]; then
    mkdir -p .streamlit
    python3 infrastructure/generate_streamlit_secrets.py > .streamlit/secrets.toml
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    exec streamlit run app/portfolio.py --server.port $PORT --server.headless 1 "$@"
else
    exec "$command" "$@"
fi