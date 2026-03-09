#!/bin/bash
# Refresh notes.json from the zettelkasten vault
# Run this after adding/modifying notes in your vault

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Refreshing notes from zettelkasten vault..."
python3 export_notes.py

echo ""
echo "Checking git status..."
git status

echo ""
echo "Notes refreshed successfully!"
echo "To commit the changes, run:"
echo "  git add notes.json"
echo "  git commit -m 'chore: refresh notes from zettelkasten'"
echo "  git push"
