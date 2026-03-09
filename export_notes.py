#!/usr/bin/env python3
"""
Export zettelkasten notes from markdown files to JSON.
Parses YAML frontmatter and extracts note content.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any
import yaml

ZETTELKASTEN_DIR = "/sessions/upbeat-busy-keller/mnt/cerebro/cerebro/6 - zettelkasten/"
OUTPUT_FILE = "/sessions/upbeat-busy-keller/mnt/cerebro/cerebro/8 - outputs/trmnl-zettelkasten/notes.json"


def parse_markdown_file(filepath: str) -> Dict[str, Any] | None:
    """
    Parse a markdown file with YAML frontmatter.
    Returns a dict with title, type, tags, body, and source.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

    # Extract YAML frontmatter (between --- markers)
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not frontmatter_match:
        print(f"No frontmatter found in {filepath}")
        return None

    try:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
    except yaml.YAMLError as e:
        print(f"YAML parse error in {filepath}: {e}")
        return None

    # Extract body (everything after the second ---)
    body_start = frontmatter_match.end()
    body = content[body_start:].strip()

    # Extract title from filename or frontmatter
    filename = Path(filepath).stem
    title = frontmatter.get('title', filename)

    # Clean up title (remove markdown heading syntax if present)
    title = re.sub(r'^#+\s*\*?\*?', '', title).strip()

    # Get type and tags from frontmatter
    note_type = frontmatter.get('type', 'note')
    tags = frontmatter.get('tags', [])

    # Ensure tags is a list
    if isinstance(tags, str):
        tags = [tags]

    # Extract source (references from body or use filename)
    source = filename

    # Try to extract URL from references section
    references = re.findall(r'https?://[^\s]+', body)
    if references:
        source = references[0]

    # Clean up body: remove markdown syntax for clean e-ink display
    body = clean_markdown(body)

    return {
        'title': title,
        'type': note_type,
        'tags': tags if isinstance(tags, list) else [tags],
        'body': body,
        'source': source
    }


def clean_markdown(text: str) -> str:
    """
    Clean markdown formatting from text for e-ink display.
    Remove markdown syntax but preserve readability.
    """
    # Remove markdown headings
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

    # Remove bold/italic markers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)

    # Remove link syntax but keep the text
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)

    # Remove code blocks but keep content
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`(.+?)`', r'\1', text)

    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)

    # Remove blockquotes but keep text
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)

    # Remove extra whitespace
    text = re.sub(r'\n\n+', '\n\n', text)
    text = text.strip()

    return text


def export_notes() -> int:
    """
    Export all markdown notes from zettelkasten directory.
    Returns number of notes exported.
    """
    notes = []

    # Get all markdown files in zettelkasten directory
    if not os.path.exists(ZETTELKASTEN_DIR):
        print(f"Error: Zettelkasten directory not found: {ZETTELKASTEN_DIR}")
        return 0

    md_files = sorted(Path(ZETTELKASTEN_DIR).glob('*.md'))
    print(f"Found {len(md_files)} markdown files")

    for filepath in md_files:
        note = parse_markdown_file(str(filepath))
        if note:
            notes.append(note)
            print(f"✓ {note['title']}")

    # Write to JSON file
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully exported {len(notes)} notes to {OUTPUT_FILE}")
        return len(notes)
    except Exception as e:
        print(f"Error writing notes.json: {e}")
        return 0


if __name__ == '__main__':
    count = export_notes()
    exit(0 if count > 0 else 1)
