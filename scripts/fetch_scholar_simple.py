#!/usr/bin/env python3
"""
Simplified Google Scholar fetcher using direct web scraping.
Use this if the 'scholarly' package installation fails.
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup


class SimpleScholarFetcher:
    """Simple Google Scholar fetcher using web scraping."""

    def __init__(self, scholar_id: str):
        """
        Initialize the fetcher.

        Args:
            scholar_id: Google Scholar user ID
        """
        self.scholar_id = scholar_id
        self.base_url = "https://scholar.google.com/citations"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.author_info = {}
        self.publications = []

    def fetch_author_info(self) -> Dict[str, Any]:
        """Fetch basic author information."""
        print(f"Fetching author information for ID: {self.scholar_id}")

        url = f"{self.base_url}?user={self.scholar_id}&hl=en"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract name
            name_elem = soup.find('div', {'id': 'gsc_prf_in'})
            name = name_elem.text if name_elem else ''

            # Extract affiliation
            affiliation_elem = soup.find('div', {'class': 'gsc_prf_il'})
            affiliation = affiliation_elem.text if affiliation_elem else ''

            # Extract citation metrics
            metrics = {}
            stats_table = soup.find('table', {'id': 'gsc_rsb_st'})
            if stats_table:
                rows = stats_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        label = cells[0].text.strip()
                        value = cells[1].text.strip()
                        try:
                            value = int(value)
                        except:
                            pass
                        if 'Citations' in label:
                            metrics['citedby'] = value
                        elif 'h-index' in label:
                            metrics['hindex'] = value
                        elif 'i10-index' in label:
                            metrics['i10index'] = value

            # Extract research interests
            interests = []
            interests_div = soup.find('div', {'id': 'gsc_prf_int'})
            if interests_div:
                interest_links = interests_div.find_all('a')
                interests = [link.text for link in interest_links]

            self.author_info = {
                'name': name,
                'affiliation': affiliation,
                'interests': interests,
                'citedby': metrics.get('citedby', 0),
                'hindex': metrics.get('hindex', 0),
                'i10index': metrics.get('i10index', 0),
                'url': url
            }

            print(f"Author: {self.author_info['name']}")
            print(f"Affiliation: {self.author_info['affiliation']}")
            print(f"Total citations: {self.author_info['citedby']}")
            print(f"h-index: {self.author_info['hindex']}")
            print(f"i10-index: {self.author_info['i10index']}")

            return self.author_info

        except Exception as e:
            print(f"Error fetching author information: {e}")
            print("This may be due to Google Scholar rate limiting.")
            print("Try again in a few minutes, or use a VPN.")
            return {}

    def fetch_publications(self, max_publications: int = None) -> List[Dict[str, Any]]:
        """Fetch publications from Google Scholar profile."""
        print("Fetching publications...")

        url = f"{self.base_url}?user={self.scholar_id}&hl=en&cstart=0&pagesize=100"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all publication rows
            pub_rows = soup.find_all('tr', {'class': 'gsc_a_tr'})

            print(f"Found {len(pub_rows)} publications")

            if max_publications:
                pub_rows = pub_rows[:max_publications]

            for idx, row in enumerate(pub_rows, 1):
                try:
                    # Extract title
                    title_elem = row.find('a', {'class': 'gsc_a_at'})
                    title = title_elem.text if title_elem else ''

                    # Extract authors and venue
                    details_elem = row.find('div', {'class': 'gs_gray'})
                    authors = details_elem.text if details_elem else ''

                    # Get the next gray div for venue
                    if details_elem and details_elem.find_next_sibling('div'):
                        venue_elem = details_elem.find_next_sibling('div')
                        venue = venue_elem.text if venue_elem else ''
                    else:
                        venue = ''

                    # Extract year
                    year_elem = row.find('span', {'class': 'gsc_a_h'})
                    year = year_elem.text if year_elem else ''

                    # Extract citations
                    citations_elem = row.find('a', {'class': 'gsc_a_ac'})
                    citations_text = citations_elem.text if citations_elem else '0'
                    try:
                        citations = int(citations_text) if citations_text else 0
                    except:
                        citations = 0

                    pub_data = {
                        'title': title,
                        'authors': authors,
                        'venue': venue,
                        'year': year,
                        'citations': citations,
                    }

                    self.publications.append(pub_data)

                    print(f"  [{idx}/{len(pub_rows)}] {title[:60]}... ({citations} citations)")

                except Exception as e:
                    print(f"  Error parsing publication: {e}")
                    continue

            print(f"Successfully fetched {len(self.publications)} publications")
            return self.publications

        except Exception as e:
            print(f"Error fetching publications: {e}")
            print("This may be due to Google Scholar rate limiting.")
            return []

    def save_to_json(self, output_path: str = None):
        """Save fetched data to JSON file."""
        if output_path is None:
            output_path = 'data/publications.json'

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'author_info': self.author_info,
            'publications': self.publications,
            'fetched_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\nData saved to {output_path}")


def main():
    """Main function."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python fetch_scholar_simple.py <scholar_id> [max_publications]")
        print("Example: python fetch_scholar_simple.py 1vePPCkAAAAJ 20")
        sys.exit(1)

    scholar_id = sys.argv[1]
    max_pubs = int(sys.argv[2]) if len(sys.argv) > 2 else None

    print("=" * 60)
    print("Simple Google Scholar Data Fetcher")
    print("=" * 60)

    fetcher = SimpleScholarFetcher(scholar_id)

    # Fetch author info
    author_info = fetcher.fetch_author_info()

    if not author_info:
        print("Failed to fetch author information. Exiting.")
        sys.exit(1)

    print("\n" + "=" * 60)

    # Fetch publications
    publications = fetcher.fetch_publications(max_publications=max_pubs)

    # Save to JSON
    fetcher.save_to_json()

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Author: {author_info['name']}")
    print(f"Publications fetched: {len(publications)}")
    print(f"Total citations: {author_info['citedby']}")
    print(f"h-index: {author_info['hindex']}")
    print(f"i10-index: {author_info['i10index']}")


if __name__ == '__main__':
    main()
