# TRMNL Zettelkasten Plugin

Automatically push random notes from your zettelkasten to a TRMNL e-ink display every 20 minutes using GitHub Actions.

## What It Does

- Selects a random note from your zettelkasten vault every 20 minutes
- Sends it to your TRMNL device via webhook
- Strips markdown formatting for clean e-ink display
- Respects TRMNL's 2KB payload limit
- Designed for 800x480 e-ink displays

## Prerequisites

- A TRMNL e-ink display device
- A TRMNL account (https://usetrmnl.com)
- A GitHub account with repository access
- Python 3.11+ (for local testing)

## Setup Instructions

### Step 1: Prepare Your TRMNL Device

1. Log in to your TRMNL account at https://usetrmnl.com
2. Go to **Plugins** → **Private Plugin** → **New**
3. Choose **Strategy: Webhook**
4. Give it a name (e.g., "Zettelkasten Notes")
5. Copy the **Plugin UUID** (you'll need this soon)
6. Click **Create**

### Step 2: Fork This Repository

1. Click "Fork" on GitHub to create your own copy
2. Clone it locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/trmnl-zettelkasten.git
   cd trmnl-zettelkasten
   ```

### Step 3: Add GitHub Actions Secret

1. Go to your forked repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `TRMNL_PLUGIN_UUID`
5. Value: Paste the UUID you copied from Step 1
6. Click **Add secret**

### Step 4: Configure TRMNL Markup Template

1. Go back to your TRMNL plugin (Plugins → Private Plugin → Your Plugin)
2. Click **Edit Markup**
3. Copy the entire contents of `TRMNL_MARKUP.html` from this repository
4. Paste it into the TRMNL markup editor
5. Save

### Step 5: Test the Setup

You have two options:

**Option A: Manual Trigger (Recommended for first test)**
1. Go to your repository on GitHub
2. Click **Actions** → **Push Note to TRMNL**
3. Click **Run workflow**
4. Check your TRMNL display (should update within a few seconds)

**Option B: Local Test**
```bash
# Install dependencies
pip install requests

# Set your UUID and run
export TRMNL_PLUGIN_UUID="your-uuid-here"
python3 push_note.py
```

### Step 6: Automatic Scheduling

Once you've confirmed the manual test works, the workflow will automatically:
- Run every 20 minutes (configured via GitHub Actions)
- Trigger on workflow_dispatch (manual button in GitHub UI)
- Push a random note to your TRMNL each time

## File Structure

```
trmnl-zettelkasten/
├── notes.json                          # Exported notes from your zettelkasten
├── export_notes.py                     # Script to export notes from vault
├── push_note.py                        # Script to push a random note to TRMNL
├── refresh_notes.sh                    # Helper script to re-export notes
├── TRMNL_MARKUP.html                   # Liquid template for TRMNL display
├── .github/workflows/push-note.yml     # GitHub Actions workflow
└── README.md                           # This file
```

## Updating Notes

When you add new notes to your zettelkasten vault and want them in the rotation:

### Option 1: Run Locally
```bash
./refresh_notes.sh
git add notes.json
git commit -m "chore: refresh notes from zettelkasten"
git push
```

### Option 2: GitHub Actions
You can create an additional workflow to auto-sync notes on a schedule (daily at midnight):
```yaml
name: Refresh Notes Daily
on:
  schedule:
    - cron: '0 0 * * *'
jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python3 export_notes.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: 'chore: refresh notes'
          file_pattern: notes.json
```

## Understanding the Code

### `export_notes.py`
- Reads all `.md` files from your zettelkasten directory
- Parses YAML frontmatter (title, type, tags, etc.)
- Extracts and cleans markdown body text
- Outputs a single `notes.json` with all notes

### `push_note.py`
- Loads notes from `notes.json`
- Picks a random note
- Truncates body to fit TRMNL's 2KB payload limit
- Sends POST request to TRMNL webhook endpoint
- Prints success/failure and logs information

### `TRMNL_MARKUP.html`
- Liquid template rendered by TRMNL
- Displays title, type, tags, body, and source
- Optimized for e-ink: high contrast, readable fonts
- Uses `{{ variable }}` syntax for dynamic content

## Customization

### Change Update Frequency

Edit `.github/workflows/push-note.yml`:
```yaml
schedule:
  - cron: '*/30 * * * *'  # Every 30 minutes
  # or
  - cron: '0 * * * *'     # Every hour
  # or
  - cron: '0 9 * * *'     # Daily at 9am UTC
```

See [cron syntax guide](https://crontab.guru/) for more options.

### Customize Display Layout

Edit `TRMNL_MARKUP.html` to change:
- Font sizes, colors, spacing
- Which fields to display
- Layout structure

Available variables:
- `{{ title }}` - Note title
- `{{ type }}` - Note type (quote, story, framework, etc.)
- `{{ tags }}` - Comma-separated tags
- `{{ body }}` - Main note content
- `{{ source }}` - Source/reference URL

### Filter Notes by Type or Tags

Modify `push_note.py` in the `main()` function:
```python
# Only push quotes
notes = [n for n in notes if n.get('type') == 'quote']

# Or only notes with specific tags
notes = [n for n in notes if 'learning' in n.get('tags', [])]
```

## Troubleshooting

### Workflow won't run
- Check that GitHub Actions are enabled (Settings → Actions)
- Verify `TRMNL_PLUGIN_UUID` secret is set correctly
- Check that cron syntax is valid at https://crontab.guru/

### Notes not appearing on TRMNL
- Verify UUID secret is correct (run manual workflow test)
- Check TRMNL markup is properly configured
- View workflow logs on GitHub (Actions tab)
- Check that TRMNL device is online and connected

### Payload size errors
- `push_note.py` automatically truncates notes to fit
- If still too large, reduce `MAX_BODY_LENGTH` in the script
- Some notes may be skipped entirely if title + tags exceed limit

### Python import errors
- Run: `pip install requests`
- Ensure Python 3.11+ is installed

## Rate Limiting

TRMNL allows up to 12 requests/hour. This workflow sends every 20 minutes (3/hour), leaving comfortable headroom for manual tests.

If you want to push more frequently, contact TRMNL support for rate limit increases.

## Advanced: Custom Filtering

You can modify `push_note.py` to implement smarter filtering:

```python
def should_include_note(note):
    # Skip notes with empty bodies
    if not note.get('body', '').strip():
        return False

    # Only quotes and stories
    if note.get('type') not in ['quote', 'story']:
        return False

    return True

# In main():
notes = [n for n in notes if should_include_note(n)]
```

## License

MIT - Use freely, modify as needed.

## Support

If you encounter issues:
1. Check the GitHub Actions logs (Actions tab)
2. Run `python3 push_note.py` locally to debug
3. Verify TRMNL plugin configuration
4. Check that `notes.json` is valid JSON

## Credits

Built for [TRMNL](https://usetrmnl.com) e-ink displays and your personal knowledge management system.
