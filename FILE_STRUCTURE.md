# File Structure and Purpose

## Root Directory Files

### Core Scripts
- **`push_note.py`** (335 lines)
  - Main script that runs every 20 minutes via GitHub Actions
  - Loads notes.json, picks a random note
  - Sends to TRMNL webhook endpoint
  - Handles payload size limits, markdown cleanup
  - Includes verbose logging for debugging

- **`export_notes.py`** (188 lines)
  - One-time or periodic export script
  - Reads all .md files from your zettelkasten vault
  - Parses YAML frontmatter (title, type, tags, etc.)
  - Cleans markdown formatting from body text
  - Outputs notes.json with all notes

- **`refresh_notes.sh`** (17 lines)
  - Bash wrapper for export_notes.py
  - Useful for manual refreshes or cron jobs
  - Shows git status and next steps

### Data
- **`notes.json`** (AUTO-GENERATED)
  - JSON array of all 529 zettelkasten notes
  - Format: `[{"title": "...", "type": "...", "tags": [...], "body": "...", "source": "..."}]`
  - Updated by running export_notes.py
  - Do NOT manually edit - regenerate by running export script

### Configuration & Templates
- **`TRMNL_MARKUP.html`** (55 lines)
  - Liquid template for TRMNL's markup editor
  - Defines how notes are displayed on the e-ink device
  - Variables: `{{ title }}`, `{{ type }}`, `{{ tags }}`, `{{ body }}`, `{{ source }}`
  - Optimized for 800x480 e-ink display
  - Uses Shopify Liquid syntax (Jinja-like)

### Documentation
- **`README.md`** (350+ lines)
  - Comprehensive guide with all features
  - Detailed setup instructions
  - Customization examples
  - Troubleshooting guide
  - Advanced usage patterns

- **`SETUP.md`** (300+ lines)
  - Step-by-step walkthrough
  - Broken into 5 parts (TRMNL setup, GitHub setup, testing, automation, updates)
  - Includes screenshots-friendly instructions
  - Detailed logging explanations
  - Best for first-time setup

- **`QUICKSTART.md`** (80 lines)
  - Ultra-condensed 5-minute quick start
  - TL;DR for experienced users
  - Fast reference for common changes
  - Minimal explanation, maximum speed

- **`.gitignore`** (25 lines)
  - Standard Python .gitignore
  - Ignores __pycache__, virtual envs, IDE files
  - Prevents accidental commits of .env files

- **`FILE_STRUCTURE.md`** (This file)
  - Index of all files with purposes
  - Line counts and descriptions
  - Quick reference guide

## .github/ Directory

### .github/workflows/push-note.yml (20 lines)
GitHub Actions workflow configuration
- Trigger: Every 20 minutes (cron: `*/20 * * * *`)
- Trigger: Manual via workflow_dispatch button
- Jobs: Single job that:
  1. Checks out the repository
  2. Sets up Python 3.11
  3. Installs requests library
  4. Runs push_note.py with TRMNL_PLUGIN_UUID secret

## How Files Interact

```
GitHub Actions (every 20 min)
    ↓
.github/workflows/push-note.yml
    ↓
runs: push_note.py
    ↓
reads: notes.json
    ↓
picks: random note
    ↓
POST to: https://usetrmnl.com/api/custom_plugins/{UUID}
    ↓
TRMNL Device (renders with TRMNL_MARKUP.html)
    ↓
Displays: Note on e-ink display
```

When updating notes:
```
Your Zettelkasten (.md files)
    ↓
run: export_notes.py (or refresh_notes.sh)
    ↓
generates: notes.json
    ↓
git commit + git push
    ↓
next workflow run uses updated notes.json
```

## File Statistics

| File | Lines | Purpose |
|------|-------|---------|
| push_note.py | 335 | Push to TRMNL |
| export_notes.py | 188 | Export zettelkasten |
| README.md | 350+ | Full documentation |
| SETUP.md | 300+ | Setup walkthrough |
| TRMNL_MARKUP.html | 55 | Display template |
| QUICKSTART.md | 80 | Quick reference |
| refresh_notes.sh | 17 | Helper script |
| .gitignore | 25 | Git configuration |
| notes.json | ~50KB | Auto-generated data |

**Total:** ~950 lines of code + docs + 529 notes

## Getting Started

1. **First time?** → Read `QUICKSTART.md` (5 min) then `SETUP.md` for details
2. **Want everything?** → Read `README.md`
3. **Troubleshooting?** → Check `README.md` troubleshooting section
4. **Need quick reference?** → This file

## File Permissions

- `push_note.py` - executable (run by GitHub Actions)
- `export_notes.py` - executable (run locally or by workflows)
- `refresh_notes.sh` - executable (bash script for manual refresh)
- All .md files - read-only documentation

## Before You Deploy

Ensure you have:
1. Created TRMNL private plugin
2. Copied plugin UUID
3. Pasted TRMNL_MARKUP.html into plugin markup editor
4. Added TRMNL_PLUGIN_UUID as GitHub secret
5. Run manual workflow test

All files are ready - no modifications needed unless you want to customize!
