#!/bin/bash

# Script to fix missing end-of-file newlines in the add-tests branch
# This fixes the CI pre-commit failures

set -e

echo "=== Fixing End-of-File Issues for CI ==="
echo

# Check if we're in the right repository
if [ ! -f "script.py" ]; then
    echo "Error: This script must be run from the repository root"
    exit 1
fi

# Save current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"

# Check if add-tests branch exists
if ! git show-ref --verify --quiet refs/heads/add-tests; then
    echo "Fetching add-tests branch from PR #4..."
    git fetch origin +refs/pull/4/head:add-tests
fi

echo "Checking out add-tests branch..."
git checkout add-tests

echo
echo "Installing pre-commit..."
pip install pre-commit --quiet

echo
echo "Running pre-commit to fix end-of-file issues..."
pre-commit run --all-files

echo
echo "Checking if there are changes to commit..."
if git diff --quiet; then
    echo "✓ No changes needed - all files already have proper end-of-file newlines!"
else
    echo "Committing fixes..."
    git add -A
    git commit -m "fix: add missing newlines at end of files for pre-commit checks"
    
    echo
    echo "✓ Changes committed successfully!"
    echo
    echo "To push these changes, run:"
    echo "  git push origin add-tests"
    echo
    echo "Or if you're working with a fork:"
    echo "  git push <your-remote> add-tests"
fi

echo
echo "Switching back to $CURRENT_BRANCH..."
git checkout "$CURRENT_BRANCH"

echo
echo "=== Done! ==="
echo
echo "The end-of-file issues have been fixed on the add-tests branch."
echo "Push the changes to trigger a new CI build that should pass."
