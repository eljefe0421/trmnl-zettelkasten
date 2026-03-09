#!/usr/bin/env python3
"""
Push a random zettelkasten note to TRMNL e-ink display via webhook.
Designed to run on GitHub Actions every 20 minutes.
"""

import json
import random
import requests
import os
import sys
from datetime import datetime

NOTES_FILE = os.path.join(os.path.dirname(__file__), 'notes.json')
TRMNL_ENDPOINT = 'https://trmnl.com/api/custom_plugins'
MAX_PAYLOAD_SIZE = 2048  # 2KB limit
MAX_BODY_LENGTH = 500  # Characters to keep body under


def load_notes() -> list[dict]:
    """Load notes from notes.json file."""
    try:
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        if not notes:
            print("Error: notes.json is empty")
            sys.exit(1)
        return notes
    except FileNotFoundError:
        print(f"Error: notes.json not found at {NOTES_FILE}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: notes.json is not valid JSON")
        sys.exit(1)


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to max_length, preserving word boundaries."""
    if len(text) <= max_length:
        return text

    truncated = text[:max_length]
    # Find last space to preserve word boundaries
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.7:  # Only if we can cut meaningfully
        truncated = truncated[:last_space]

    return truncated.rstrip() + '...'


def format_tags(tags: list) -> str:
    """Format tags into a comma-separated string."""
    if not tags:
        return ""
    return ", ".join(str(tag) for tag in tags[:5])  # Limit to 5 tags


def build_payload(note: dict) -> dict:
    """
    Build the webhook payload for TRMNL.
    Ensures payload stays under 2KB limit.
    """
    merge_variables = {
        'title': note.get('title', 'Untitled')[:100],  # Limit title
        'type': note.get('type', 'note')[:30],
        'tags': format_tags(note.get('tags', [])),
        'body': truncate_text(note.get('body', ''), MAX_BODY_LENGTH),
        'source': str(note.get('source', 'Unknown'))[:100],
    }

    payload = {'merge_variables': merge_variables}

    # Verify payload size
    payload_json = json.dumps(payload)
    payload_size = len(payload_json.encode('utf-8'))

    if payload_size > MAX_PAYLOAD_SIZE:
        print(f"Warning: Payload size ({payload_size} bytes) exceeds 2KB limit")
        # Aggressively truncate body
        merge_variables['body'] = truncate_text(
            merge_variables['body'], int(MAX_BODY_LENGTH * 0.5)
        )
        payload = {'merge_variables': merge_variables}

    return payload


def push_to_trmnl(plugin_uuid: str, payload: dict) -> bool:
    """Push the payload to TRMNL webhook endpoint."""
    if not plugin_uuid:
        print("Error: TRMNL_PLUGIN_UUID environment variable not set")
        return False

    url = f"{TRMNL_ENDPOINT}/{plugin_uuid}"
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"Success: HTTP {response.status_code}")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {response.status_code}")
        try:
            print(f"Response: {response.text}")
        except Exception:
            pass
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error pushing to TRMNL: {e}")
        return False


def main():
    """Main execution."""
    plugin_uuid = os.getenv('TRMNL_PLUGIN_UUID')

    print("=" * 60)
    print(f"TRMNL Zettelkasten Plugin - {datetime.now().isoformat()}")
    print("=" * 60)

    # Load notes
    notes = load_notes()
    print(f"Loaded {len(notes)} notes from notes.json")

    # Pick random note
    note = random.choice(notes)
    print(f"\nSelected note:")
    print(f"  Title: {note.get('title', 'Untitled')}")
    print(f"  Type: {note.get('type', 'note')}")
    print(f"  Tags: {format_tags(note.get('tags', []))}")
    print(f"  Source: {note.get('source', 'Unknown')}")
    print(f"  Body length: {len(note.get('body', ''))} chars")

    # Build and push payload
    payload = build_payload(note)
    payload_size = len(json.dumps(payload).encode('utf-8'))
    print(f"\nPayload size: {payload_size} bytes")

    if not plugin_uuid:
        print("\nError: TRMNL_PLUGIN_UUID not set (running locally?)")
        print("Payload that would be sent:")
        print(json.dumps(payload, indent=2))
        return

    print(f"\nPushing to TRMNL ({plugin_uuid[:8]}...)...")
    success = push_to_trmnl(plugin_uuid, payload)

    if success:
        print("\n✓ Note pushed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Failed to push note")
        sys.exit(1)


if __name__ == '__main__':
    main()
