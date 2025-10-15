#!/bin/bash

# recovery-guide.sh - Show available recovery options

echo "🛡️  RECOVERY OPTIONS AVAILABLE:"
echo "================================="

echo ""
echo "📋 Current Status:"
git status --short

echo ""
echo "🏷️  Available Milestone Tags:"
git tag -l "milestone-*" | tail -5

echo ""
echo "🌿 Available Backup Branches:"
git branch -r | grep "backup-before-" | tail -5

echo ""
echo "📝 Recent Commits (last 5):"
git log --oneline -5

echo ""
echo "🔄 QUICK RECOVERY COMMANDS:"
echo "=========================="
echo "• git checkout main                    # Back to latest main"
echo "• git checkout milestone-YYYYMMDD-HHMM # Back to specific milestone"
echo "• git checkout backup-before-[name]    # Back to backup branch"
echo "• git reset --hard origin/main         # Nuclear option (discard all local changes)"

echo ""
echo "💡 TIP: Use these scripts for easy development:"
echo "• ./save-progress.sh 'description'     # Save current progress"
echo "• ./create-milestone.sh 'description'  # Create milestone"
echo "• ./backup-before-changes.sh 'name'    # Backup before risky changes"
