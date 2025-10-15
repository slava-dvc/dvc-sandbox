#!/bin/bash

# backup-before-changes.sh - Create backup branch before risky changes
# Usage: ./backup-before-changes.sh "feature-name"

if [ $# -eq 0 ]; then
    echo "Usage: ./backup-before-changes.sh 'feature-name'"
    echo "Example: ./backup-before-changes.sh 'user-authentication'"
    exit 1
fi

FEATURE_NAME="$1"
TIMESTAMP=$(date '+%Y%m%d-%H%M')
BRANCH_NAME="backup-before-$FEATURE_NAME-$TIMESTAMP"

echo "💾 Creating backup branch before working on: $FEATURE_NAME"

# Create and switch to backup branch
git checkout -b "$BRANCH_NAME"

# Push backup branch to remote
git push origin "$BRANCH_NAME"

echo "✅ Backup branch created successfully!"
echo "🌿 Branch name: $BRANCH_NAME"
echo "🔄 You can recover from this backup with: git checkout $BRANCH_NAME"

# Switch back to main for development
git checkout main

echo "📝 You're now on main branch and ready to develop $FEATURE_NAME"
echo "💡 Remember to create progress commits as you work!"
