#!/bin/bash
set -e

# Store the first argument
command="$1"
# Shift once to remove the first argument
shift

if [ "$command" = 'backend' ]; then
    exec python -m app.backend "$@"
elif [ "$command" = 'job' ]; then
    exec python -m app.job "$@"
elif [ "$command" = "portfolio" ]; then
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    exec streamlit run app/portfolio.py "$@"
else
    exec "$command" "$@"
fi