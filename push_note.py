#!/usr/bin/env python3
"""Push a random zettelkasten note to TRMNL e-ink display via webhook."""

import json
import random
import requests
import os
import sys
from datetime import datetime

NOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes.json')
TRMNL_ENDPOINT = 'https://trmnl.com/api/custom_plugins'
MAX_BODY_LENGTH = 500

def load_notes():
    with open(NOTES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def truncate_text(text, max_length):
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.7:
        truncated = truncated[:last_space]
    return truncated.rstrip() + '...'

def main():
    plugin_uuid = os.getenv('TRMNL_PLUGIN_UUID')
    if not plugin_uuid:
        print("Error: TRMNL_PLUGIN_UUID not set")
        sys.exit(1)

    notes = load_notes()
    note = random.choice(notes)

    title = note.get('title', 'Untitled')
    body = note.get('body', '')

    # Strip the repeated title from the start of the body
    for sep in ['\n\n', '\n']:
        if body.lower().startswith(title.lower()[:20]):
            idx = body.find(sep)
            if idx != -1:
                body = body[idx:].lstrip('\n')
                break

    payload = {
        'merge_variables': {
            'title': title[:100],
            'type': note.get('type', 'note')[:30],
            'body': truncate_text(body, MAX_BODY_LENGTH),
            'source': '',
        }
    }

    print(f"Pushing: {note.get('title', 'Untitled')}")
    url = f"{TRMNL_ENDPOINT}/{plugin_uuid}"
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
    response.raise_for_status()
    print(f"Success: HTTP {response.status_code}")

if __name__ == '__main__':
    main()
