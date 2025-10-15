#!/bin/bash

# save-progress.sh - Quick progress saving script
# Usage: ./save-progress.sh "description of what you just completed"

if [ $# -eq 0 ]; then
    echo "Usage: ./save-progress.sh 'description of progress'"
    echo "Example: ./save-progress.sh 'added task filtering feature'"
    exit 1
fi

PROGRESS_DESC="$1"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

echo "🚀 Saving progress: $PROGRESS_DESC"

# Add all changes
git add .

# Commit with timestamp and description
git commit -m "progress: $TIMESTAMP - $PROGRESS_DESC"

# Push to remote
git push origin main

echo "✅ Progress saved successfully!"
echo "📝 Commit message: progress: $TIMESTAMP - $PROGRESS_DESC"
echo "🔄 You can recover from this point anytime with: git checkout main"
