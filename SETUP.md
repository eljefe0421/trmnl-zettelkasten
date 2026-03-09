# TRMNL Zettelkasten Plugin - Detailed Setup Guide

This is a step-by-step walkthrough to get your TRMNL display showing random zettelkasten notes every 20 minutes.

## Prerequisites Checklist

- [ ] TRMNL e-ink display device (already owned)
- [ ] TRMNL account created at https://usetrmnl.com
- [ ] GitHub account (free tier is fine)
- [ ] This repository cloned or forked

## Step-by-Step Setup

### Part 1: TRMNL Device Configuration (5 minutes)

#### 1.1 Create a Private Plugin

1. Log into your TRMNL account
2. Navigate to **Plugins** section
3. Click **Private Plugin** → **New**
4. Configure:
   - **Name**: "Zettelkasten Notes" (or your preferred name)
   - **Description**: "Random notes from my personal knowledge base"
   - **Strategy**: Select **Webhook** from dropdown

#### 1.2 Copy Your Plugin UUID

After creating the plugin:
- You'll see a **Plugin UUID** displayed (looks like: `abc123def456...`)
- Copy this UUID - you'll need it in the next step
- **Important**: Keep this UUID secret! It's like a password to your plugin.

#### 1.3 Set the Markup Template

Still in your plugin:
1. Click **Edit Markup**
2. Clear any default content
3. Open `TRMNL_MARKUP.html` from this repository in a text editor
4. Copy the entire file contents
5. Paste into the TRMNL markup editor
6. Click **Save**

The template uses Liquid syntax (`{{ variable }}`) to display:
- Title (note headline)
- Type (quote, story, framework, etc.)
- Tags (comma-separated)
- Body (main note content, cleaned of markdown)
- Source (original reference)

### Part 2: GitHub Repository Setup (10 minutes)

#### 2.1 Fork or Clone

**Option A: Fork (Recommended for first-time users)**
- Click "Fork" on the GitHub repository
- This creates your own copy under your account
- You'll have full control to customize later

**Option B: Clone**
```bash
git clone https://github.com/YOUR-USERNAME/trmnl-zettelkasten.git
cd trmnl-zettelkasten
```

#### 2.2 Add the Secret

This is how GitHub Actions accesses your TRMNL plugin securely.

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click the **New repository secret** button
5. Fill in:
   - **Name**: `TRMNL_PLUGIN_UUID`
   - **Value**: Paste the UUID from Step 1.2
6. Click **Add secret**

**Note**: This secret is encrypted and only used by GitHub Actions. You won't see it again.

### Part 3: Test the Setup (5 minutes)

#### 3.1 Manual Workflow Test

This is the safest way to verify everything works before automation starts.

1. Go to your GitHub repository
2. Click the **Actions** tab (top menu)
3. In the left sidebar, click **Push Note to TRMNL**
4. Click the **Run workflow** button
5. Select **Branch: main** (or your main branch)
6. Click **Run workflow**

The workflow should:
- Start in a few seconds
- Show a green checkmark when complete
- Push a random note to your TRMNL display

**Check your TRMNL display** - it should update within 10 seconds with a random note!

#### 3.2 Check the Logs (Optional)

To see what the script did:

1. In the Actions tab, click the **Push Note to TRMNL** workflow run
2. Click the **push-note** job
3. Click the **Pick random note and push to TRMNL** step
4. You'll see output like:
   ```
   Loaded 529 notes from notes.json
   Selected note:
     Title: [note title]
     Type: [quote/story/etc]
     Tags: [tag1, tag2, ...]
     Body length: XXX chars
   Payload size: XXX bytes
   Success: HTTP 200
   ✓ Note pushed successfully!
   ```

### Part 4: Automatic Scheduling (2 minutes)

Once you've verified the manual test works, **automatic scheduling is already enabled**!

The workflow is configured to run every 20 minutes. You don't need to do anything else.

**Check the schedule:**
1. Go to **Actions** tab
2. Click **Push Note to TRMNL** workflow
3. You'll see "This workflow has a schedule" with the cron expression
4. Next scheduled run time is displayed

### Part 5: Update Your Notes (Optional, but recommended)

When you add new notes to your zettelkasten vault, refresh the plugin's list:

#### Option A: Manual Refresh (One-time)

```bash
# In the repository directory
python3 export_notes.py

# This updates notes.json with new notes
git add notes.json
git commit -m "chore: refresh notes from zettelkasten"
git push
```

#### Option B: Automatic Daily Refresh

Create a new GitHub Actions workflow to automatically export notes daily. Create a file:
`.github/workflows/daily-refresh.yml`

```yaml
name: Daily Refresh Notes

on:
  schedule:
    - cron: '0 0 * * *'  # Midnight UTC daily
  workflow_dispatch:

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Export notes
        run: python3 export_notes.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: 'chore: refresh notes daily'
          file_pattern: notes.json
```

## Troubleshooting

### "Workflow won't start"
- GitHub Actions are enabled by default. Check **Settings** → **Actions** if disabled
- Verify cron schedule is valid at https://crontab.guru/

### "Note doesn't appear on TRMNL"
1. Manually run the workflow (Part 3.1)
2. Check the action logs for errors
3. Verify the TRMNL_PLUGIN_UUID secret is correct
4. Confirm TRMNL markup was updated in Step 1.3

### "Getting HTTP 401 errors"
- The TRMNL_PLUGIN_UUID secret is wrong or expired
- Create a new plugin UUID and update the secret

### "Getting HTTP 404 errors"
- The plugin UUID doesn't exist
- Regenerate it in TRMNL and update the secret

### "Notes look ugly on display"
- Edit `TRMNL_MARKUP.html` to adjust fonts, spacing, colors
- Test by manually running the workflow

### "Script runs but nothing happens"
- Check that TRMNL is connected and powered on
- Verify the plugin UUID is correct
- Try a manual test with a different browser

## Next Steps

Once everything is working:

1. **Customize the display** - Edit `TRMNL_MARKUP.html` for different layouts
2. **Change update frequency** - Edit `.github/workflows/push-note.yml` cron time
3. **Filter notes** - Modify `push_note.py` to only show certain types or tags
4. **Auto-refresh** - Set up daily note export from your vault

## Understanding What's Running

### Every 20 Minutes (via GitHub Actions)
1. GitHub runs `push_note.py`
2. Script loads `notes.json` (529 notes from your zettelkasten)
3. Picks a random note
4. Strips markdown formatting
5. Sends to TRMNL via webhook
6. TRMNL displays it using the Liquid template

### When You Update Notes
1. Run `export_notes.py` locally or via workflow
2. It reads all `.md` files from your zettelkasten
3. Parses YAML frontmatter (title, type, tags)
4. Cleans markdown from body
5. Writes to `notes.json`
6. Commit and push to GitHub

## Performance Notes

- **Payload size**: Averaged 400-600 bytes (well under 2KB limit)
- **API rate limit**: TRMNL allows 12 requests/hour; this uses 3 (20-min interval)
- **Note count**: Successfully loaded and rotating through 529 notes
- **Processing time**: < 1 second per push

## Advanced Customization

See the README.md for:
- Filtering notes by type or tags
- Changing display frequency
- Custom display layouts
- Setting up auto-sync workflows

## Getting Help

If you run into issues:

1. Check the GitHub Actions logs (Actions tab → workflow run → job)
2. Run locally: `TRMNL_PLUGIN_UUID=your-uuid python3 push_note.py`
3. Verify notes.json is valid JSON: `python3 -m json.tool notes.json | head`
4. Check TRMNL dashboard for recent activity

---

**Congratulations!** Your TRMNL display should now show a random zettelkasten note every 20 minutes. Enjoy your continuous learning!
