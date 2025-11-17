#!/usr/bin/env python3
"""
Fetch publication data from Google Scholar.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any
from scholarly import scholarly, ProxyGenerator


class ScholarFetcher:
    """Fetcher for Google Scholar data."""

    def __init__(self, scholar_id: str, use_proxy: bool = False):
        """
        Initialize the Scholar fetcher.

        Args:
            scholar_id: Google Scholar user ID
            use_proxy: Whether to use proxy (helps avoid rate limiting)
        """
        self.scholar_id = scholar_id
        self.publications = []
        self.author_info = {}

        if use_proxy:
            self._setup_proxy()

    def _setup_proxy(self):
        """Setup proxy to avoid rate limiting."""
        try:
            pg = ProxyGenerator()
            pg.FreeProxies()
            scholarly.use_proxy(pg)
            print("Proxy setup successful")
        except Exception as e:
            print(f"Warning: Could not setup proxy: {e}")
            print("Continuing without proxy (may be rate limited)")

    def fetch_author_info(self) -> Dict[str, Any]:
        """
        Fetch author information from Google Scholar.

        Returns:
            Dictionary with author information
        """
        print(f"Fetching author information for ID: {self.scholar_id}")

        try:
            author = scholarly.search_author_id(self.scholar_id)
            author = scholarly.fill(author, sections=['basics', 'indices', 'counts'])

            self.author_info = {
                'name': author.get('name', ''),
                'affiliation': author.get('affiliation', ''),
                'interests': author.get('interests', []),
                'citedby': author.get('citedby', 0),
                'citedby5y': author.get('citedby5y', 0),
                'hindex': author.get('hindex', 0),
                'hindex5y': author.get('hindex5y', 0),
                'i10index': author.get('i10index', 0),
                'i10index5y': author.get('i10index5y', 0),
                'cites_per_year': author.get('cites_per_year', {}),
                'url': f"https://scholar.google.com/citations?user={self.scholar_id}"
            }

            print(f"Author: {self.author_info['name']}")
            print(f"Affiliation: {self.author_info['affiliation']}")
            print(f"Total citations: {self.author_info['citedby']}")
            print(f"h-index: {self.author_info['hindex']}")

            return self.author_info

        except Exception as e:
            print(f"Error fetching author information: {e}")
            return {}

    def fetch_publications(self, max_publications: int = None) -> List[Dict[str, Any]]:
        """
        Fetch publications from Google Scholar.

        Args:
            max_publications: Maximum number of publications to fetch (None = all)

        Returns:
            List of publication dictionaries
        """
        print("Fetching publications...")

        try:
            author = scholarly.search_author_id(self.scholar_id)
            author = scholarly.fill(author, sections=['publications'])

            publications = author.get('publications', [])
            total = len(publications)
            print(f"Found {total} publications")

            if max_publications:
                publications = publications[:max_publications]
                print(f"Fetching details for first {max_publications} publications")

            for idx, pub in enumerate(publications, 1):
                try:
                    print(f"  [{idx}/{len(publications)}] Fetching: {pub['bib'].get('title', 'Unknown')[:60]}...")

                    # Fill in publication details
                    filled_pub = scholarly.fill(pub)

                    pub_data = {
                        'title': filled_pub['bib'].get('title', ''),
                        'authors': filled_pub['bib'].get('author', ''),
                        'year': filled_pub['bib'].get('pub_year', ''),
                        'venue': filled_pub['bib'].get('venue', ''),
                        'publisher': filled_pub['bib'].get('publisher', ''),
                        'citations': filled_pub.get('num_citations', 0),
                        'url': filled_pub.get('pub_url', ''),
                        'author_pub_id': filled_pub.get('author_pub_id', ''),
                        'abstract': filled_pub['bib'].get('abstract', ''),
                    }

                    self.publications.append(pub_data)

                    # Be nice to Google Scholar - add delay
                    time.sleep(2)

                except Exception as e:
                    print(f"    Warning: Could not fetch details for publication: {e}")
                    # Add basic info even if full fetch fails
                    self.publications.append({
                        'title': pub['bib'].get('title', ''),
                        'authors': pub['bib'].get('author', ''),
                        'year': pub['bib'].get('pub_year', ''),
                        'citations': pub.get('num_citations', 0),
                    })

            print(f"Successfully fetched {len(self.publications)} publications")
            return self.publications

        except Exception as e:
            print(f"Error fetching publications: {e}")
            return []

    def save_to_json(self, output_path: str = None):
        """
        Save fetched data to JSON file.

        Args:
            output_path: Path to save JSON file (default: data/publications.json)
        """
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

    def get_formatted_publications(self, format: str = 'apa') -> List[str]:
        """
        Get publications formatted in various citation styles.

        Args:
            format: Citation format ('apa', 'mla', 'chicago', 'simple')

        Returns:
            List of formatted citations
        """
        formatted = []

        for pub in self.publications:
            if format == 'simple':
                citation = f"{pub['authors']} ({pub['year']}). {pub['title']}. {pub['venue']}."
            elif format == 'apa':
                citation = f"{pub['authors']} ({pub['year']}). {pub['title']}. {pub['venue']}."
            else:
                # Default simple format
                citation = f"{pub['authors']} ({pub['year']}). {pub['title']}. {pub['venue']}."

            if pub['citations'] > 0:
                citation += f" [Cited by {pub['citations']}]"

            formatted.append(citation)

        return formatted


def main():
    """Main function to fetch Google Scholar data."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python fetch_scholar.py <scholar_id> [max_publications]")
        print("Example: python fetch_scholar.py 1vePPCkAAAAJ 10")
        print("\nTo find your Scholar ID, visit your Google Scholar profile.")
        print("Your ID is in the URL: https://scholar.google.com/citations?user=SCHOLAR_ID")
        sys.exit(1)

    scholar_id = sys.argv[1]
    max_pubs = int(sys.argv[2]) if len(sys.argv) > 2 else None

    print("=" * 60)
    print("Google Scholar Data Fetcher")
    print("=" * 60)

    fetcher = ScholarFetcher(scholar_id, use_proxy=False)

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
