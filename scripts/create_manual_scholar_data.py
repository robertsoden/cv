#!/usr/bin/env python3
"""
Create a publications.json file manually with your Google Scholar metrics.
Use this when automated fetching fails due to Google Scholar's blocking.
"""

import json
from pathlib import Path


def create_manual_scholar_data():
    """
    Create a manual publications.json file.

    Instructions:
    1. Go to your Google Scholar profile: https://scholar.google.com/citations?user=1vePPCkAAAAJ
    2. Manually fill in the values below from your profile
    3. Run this script to create the publications data file
    """

    # TODO: Fill in these values from your Google Scholar profile
    scholar_data = {
        "author_info": {
            "name": "Robert Soden",  # Update with your name
            "affiliation": "University of Toronto",  # Update with your affiliation
            "interests": [
                "Human-Computer Interaction",
                "Disaster Risk Management",
                "Climate Change",
                "Crisis Informatics"
            ],  # Update with your research interests
            "citedby": 2500,  # Update with your total citations
            "hindex": 25,     # Update with your h-index
            "i10index": 35,   # Update with your i10-index
            "citedby5y": 2000,  # Update with citations (last 5 years)
            "hindex5y": 22,     # Update with h-index (last 5 years)
            "i10index5y": 30,   # Update with i10-index (last 5 years)
            "url": "https://scholar.google.com/citations?user=1vePPCkAAAAJ"
        },
        "publications": [],  # Will be populated from CV data
        "fetched_at": "Manually created",
        "note": "Citation data manually entered. Run this script again to update metrics."
    }

    # Load publications from cv_data.json if available
    cv_data_path = Path('data/cv_data.json')
    if cv_data_path.exists():
        with open(cv_data_path, 'r', encoding='utf-8') as f:
            cv_data = json.load(f)

        # Extract publications from CV data
        pub_texts = cv_data.get('other_sections', {}).get('publications', [])

        for pub_text in pub_texts:
            # Skip section headers
            if any(header in pub_text for header in ['MANUSCRIPTS', 'CONFERENCE', 'PATENTS', 'SCHOLARLY']):
                continue

            # Parse publication text (simple extraction)
            import re

            # Try to extract year
            year_match = re.search(r'\((\d{4})\)', pub_text)
            year = year_match.group(1) if year_match else ''

            # Try to extract authors (everything before year)
            if year_match:
                authors = pub_text[:year_match.start()].strip().rstrip(',')
            else:
                authors = ''

            # Title is usually after year
            if year_match:
                rest = pub_text[year_match.end():].strip().lstrip('.')
                # Title is usually the first sentence
                title_match = re.match(r'^([^.]+\.)', rest)
                title = title_match.group(1).strip('.') if title_match else rest
            else:
                title = pub_text[:100]  # First 100 chars as fallback

            pub_data = {
                'title': title,
                'authors': authors,
                'year': year,
                'venue': '',  # Venue extraction is more complex
                'citations': 0,  # Set to 0 - user can update manually
                'full_text': pub_text  # Keep original for reference
            }

            scholar_data['publications'].append(pub_data)

        print(f"Extracted {len(scholar_data['publications'])} publications from CV data")

    # Save to file
    output_path = Path('data/publications.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(scholar_data, f, indent=2, ensure_ascii=False)

    print(f"\nManual scholar data saved to: {output_path}")
    print("\nNext steps:")
    print("1. Edit data/publications.json to add your actual citation metrics from Google Scholar")
    print("2. Optionally add citation counts for individual publications")
    print("3. Run: python scripts/generate_cv.py")


if __name__ == '__main__':
    create_manual_scholar_data()
