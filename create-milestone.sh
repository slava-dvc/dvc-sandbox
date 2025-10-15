#!/bin/bash

# create-milestone.sh - Create a milestone tag for stable versions
# Usage: ./create-milestone.sh "description of milestone"

if [ $# -eq 0 ]; then
    echo "Usage: ./create-milestone.sh 'description of milestone'"
    echo "Example: ./create-milestone.sh 'task addition feedback complete'"
    exit 1
fi

MILESTONE_DESC="$1"
TIMESTAMP=$(date '+%Y%m%d-%H%M')
TAG_NAME="milestone-$TIMESTAMP"

echo "🏆 Creating milestone: $MILESTONE_DESC"

# Create annotated tag with description
git tag -a "$TAG_NAME" -m "Milestone: $MILESTONE_DESC

- Stable working version
- Ready for production/demo
- Created: $(date '+%Y-%m-%d %H:%M:%S')"

# Push tag to remote
git push origin "$TAG_NAME"

echo "✅ Milestone created successfully!"
echo "🏷️  Tag name: $TAG_NAME"
echo "🔄 You can recover from this milestone with: git checkout $TAG_NAME"
echo "📋 Description: $MILESTONE_DESC"
