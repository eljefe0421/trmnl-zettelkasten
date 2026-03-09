# Quick Start (5 minutes)

## TL;DR

1. **TRMNL side**: Create private plugin, copy UUID, paste markup
2. **GitHub side**: Add UUID as secret, test, done
3. **Result**: Random note every 20 minutes

## For the Impatient

### Step 1: TRMNL (2 min)
```
TRMNL → Plugins → Private Plugin → New
  Name: "Zettelkasten"
  Strategy: Webhook
  [Copy UUID]

Edit Markup → Paste TRMNL_MARKUP.html content → Save
```

### Step 2: GitHub (2 min)
```
Your repo → Settings → Secrets and variables → Actions

New secret:
  Name: TRMNL_PLUGIN_UUID
  Value: [Paste the UUID from Step 1]

Save
```

### Step 3: Test (1 min)
```
Your repo → Actions → Push Note to TRMNL → Run workflow

Wait 10 seconds...
✓ Check TRMNL display (should have a random note)
```

## Done!

Your display will automatically update every 20 minutes with a random note from your zettelkasten.

---

## If Something Breaks

1. **Verify UUID** - Did you copy it correctly? No extra spaces?
2. **Check logs** - Actions tab → workflow run → look for errors
3. **Try local test** - `TRMNL_PLUGIN_UUID=your-uuid python3 push_note.py`
4. **See detailed setup** - Read `SETUP.md` or `README.md`

---

## Common Changes

**Change frequency from 20 min to X?**
Edit `.github/workflows/push-note.yml`, change:
```yaml
- cron: '*/X * * * *'  # Every X minutes
```

**Change display layout?**
Edit `TRMNL_MARKUP.html`

**Add new notes?**
```bash
python3 export_notes.py
git add notes.json && git commit -m "refresh" && git push
```

---

That's it! Enjoy your zettelkasten on e-ink.
