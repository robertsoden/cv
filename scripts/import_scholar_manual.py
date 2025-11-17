#!/usr/bin/env python3
"""
Manually import Google Scholar publications from a text file.

Usage:
1. Go to your Google Scholar profile
2. Copy your publication list to a text file
3. Run this script to import it
"""

import json
import re
from pathlib import Path
from typing import List, Dict


def parse_scholar_text(text_file: str) -> List[Dict]:
    """
    Parse Google Scholar publications from a copied text file.

    Expected format (copy directly from Google Scholar):
    Title of paper
    Author1, Author2, Author3
    Conference/Journal, Year
    Cited by X

    or simply:
    Title
    Authors
    Venue
    """
    publications = []

    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by "Cited by" or double newlines
    entries = re.split(r'\n\s*\n', content)

    for entry in entries:
        if not entry.strip():
            continue

        lines = [line.strip() for line in entry.split('\n') if line.strip()]

        if len(lines) < 2:
            continue

        # First line is usually the title
        title = lines[0]

        # Second line is usually authors
        authors = lines[1] if len(lines) > 1 else ''

        # Third line might be venue/year
        venue = ''
        year = ''
        citations = 0

        if len(lines) > 2:
            venue_line = lines[2]

            # Extract year from venue line
            year_match = re.search(r'\b(19|20)\d{2}\b', venue_line)
            if year_match:
                year = year_match.group()
                venue = venue_line.replace(year, '').strip(', ')
            else:
                venue = venue_line

        # Look for citations
        for line in lines:
            cite_match = re.search(r'Cited by (\d+)', line)
            if cite_match:
                citations = int(cite_match.group(1))
                break

        publications.append({
            'title': title,
            'authors': authors,
            'venue': venue,
            'year': year,
            'citations': citations
        })

    return publications


def import_scholar_data(text_file: str, output_file: str = 'data/publications.json'):
    """Import Google Scholar data from text file."""
    print(f"Importing publications from: {text_file}")

    publications = parse_scholar_text(text_file)

    print(f"Found {len(publications)} publications")

    # Create the data structure
    scholar_data = {
        'author_info': {
            'name': input("Enter your name: "),
            'affiliation': input("Enter your affiliation: "),
            'interests': [],
            'citedby': int(input("Enter total citations: ") or "0"),
            'hindex': int(input("Enter h-index: ") or "0"),
            'i10index': int(input("Enter i10-index: ") or "0"),
            'url': input("Enter Google Scholar profile URL: ")
        },
        'publications': publications,
        'fetched_at': 'Manually imported',
        'import_source': text_file
    }

    # Save to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(scholar_data, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to: {output_path}")
    print(f"Imported {len(publications)} publications")
    print("\nYou can now run: python scripts/compare_publications.py")


def main():
    """Main function."""
    import sys

    if len(sys.argv) < 2:
        print("Manual Google Scholar Import")
        print("=" * 60)
        print("\nUsage: python scripts/import_scholar_manual.py <text_file>")
        print("\nHow to use:")
        print("1. Go to your Google Scholar profile")
        print("2. Select and copy your publications list")
        print("3. Paste into a text file (e.g., scholar_pubs.txt)")
        print("4. Run: python scripts/import_scholar_manual.py scholar_pubs.txt")
        print("\nAlternatively, you can create a CSV file with columns:")
        print("Title,Authors,Venue,Year,Citations")
        sys.exit(1)

    text_file = sys.argv[1]

    if not Path(text_file).exists():
        print(f"Error: File not found: {text_file}")
        sys.exit(1)

    # Check if it's a CSV
    if text_file.endswith('.csv'):
        print("CSV import not yet implemented. Use text format for now.")
        sys.exit(1)

    import_scholar_data(text_file)


if __name__ == '__main__':
    main()
