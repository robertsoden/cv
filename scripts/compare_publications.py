#!/usr/bin/env python3
"""
Compare publications between CV and Google Scholar to identify gaps and discrepancies.
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from difflib import SequenceMatcher
import re


class PublicationComparator:
    """Compare publications from different sources."""

    def __init__(self, cv_data_path: str = 'data/cv_data.json',
                 scholar_data_path: str = 'data/publications.json'):
        """Initialize comparator with data file paths."""
        self.cv_data = self._load_json(cv_data_path)
        self.scholar_data = self._load_json(scholar_data_path)

        self.cv_pubs = []
        self.scholar_pubs = []

        # Results
        self.only_in_cv = []
        self.only_in_scholar = []
        self.matched = []
        self.potential_matches = []

    def _load_json(self, path: str) -> Dict:
        """Load JSON data from file."""
        path = Path(path)
        if not path.exists():
            print(f"Warning: {path} not found.")
            return {}

        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def normalize_title(self, title: str) -> str:
        """
        Normalize title for comparison.
        - Convert to lowercase
        - Remove punctuation
        - Remove extra whitespace
        """
        # Convert to lowercase
        title = title.lower()

        # Remove common punctuation
        title = re.sub(r'[.,;:!?"\']', '', title)

        # Normalize whitespace
        title = re.sub(r'\s+', ' ', title).strip()

        return title

    def extract_cv_publications(self) -> List[Dict]:
        """Extract publications from CV data."""
        cv_pubs = []

        # Get publications from CV data
        pub_texts = self.cv_data.get('other_sections', {}).get('publications', [])

        for pub_text in pub_texts:
            # Skip section headers
            if any(header in pub_text.upper() for header in
                   ['MANUSCRIPTS', 'CONFERENCE', 'PATENTS', 'SCHOLARLY',
                    'INVITED', 'MEDIA', 'OTHER', 'UNDER REVIEW']):
                continue

            # Parse publication
            year_match = re.search(r'\((\d{4})\)', pub_text)
            year = year_match.group(1) if year_match else ''

            # Extract title (crude but works for most cases)
            if year_match:
                # Title is usually after year and first period
                rest = pub_text[year_match.end():].strip()
                # Find first sentence as title
                title_match = re.match(r'^\.?\s*([^.]+)', rest)
                title = title_match.group(1).strip() if title_match else rest[:100]
            else:
                title = pub_text[:100]

            cv_pubs.append({
                'title': title,
                'title_normalized': self.normalize_title(title),
                'year': year,
                'full_text': pub_text,
                'source': 'cv'
            })

        self.cv_pubs = cv_pubs
        return cv_pubs

    def extract_scholar_publications(self) -> List[Dict]:
        """Extract publications from Google Scholar data."""
        scholar_pubs = []

        pubs = self.scholar_data.get('publications', [])

        for pub in pubs:
            # Skip if it's from CV (created by manual script)
            if pub.get('full_text'):
                continue

            title = pub.get('title', '')

            scholar_pubs.append({
                'title': title,
                'title_normalized': self.normalize_title(title),
                'year': str(pub.get('year', '')),
                'authors': pub.get('authors', ''),
                'venue': pub.get('venue', ''),
                'citations': pub.get('citations', 0),
                'source': 'scholar'
            })

        self.scholar_pubs = scholar_pubs
        return scholar_pubs

    def similarity_score(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings (0-1)."""
        return SequenceMatcher(None, str1, str2).ratio()

    def find_matches(self, threshold: float = 0.85,
                    potential_threshold: float = 0.65) -> None:
        """
        Find matches between CV and Scholar publications.

        Args:
            threshold: Similarity threshold for definite matches (default 0.85)
            potential_threshold: Threshold for potential matches (default 0.65)
        """
        cv_matched_indices = set()
        scholar_matched_indices = set()

        # Find definite matches
        for i, cv_pub in enumerate(self.cv_pubs):
            best_score = 0
            best_match_idx = -1

            for j, scholar_pub in enumerate(self.scholar_pubs):
                if j in scholar_matched_indices:
                    continue

                # Compare normalized titles
                score = self.similarity_score(
                    cv_pub['title_normalized'],
                    scholar_pub['title_normalized']
                )

                # Also check if years match (if both have years)
                if cv_pub['year'] and scholar_pub['year']:
                    if cv_pub['year'] != scholar_pub['year']:
                        score *= 0.7  # Penalize year mismatch

                if score > best_score:
                    best_score = score
                    best_match_idx = j

            # Categorize based on score
            if best_score >= threshold:
                # Definite match
                self.matched.append({
                    'cv': cv_pub,
                    'scholar': self.scholar_pubs[best_match_idx],
                    'score': best_score
                })
                cv_matched_indices.add(i)
                scholar_matched_indices.add(best_match_idx)
            elif best_score >= potential_threshold:
                # Potential match (needs review)
                self.potential_matches.append({
                    'cv': cv_pub,
                    'scholar': self.scholar_pubs[best_match_idx],
                    'score': best_score
                })
                cv_matched_indices.add(i)
                scholar_matched_indices.add(best_match_idx)

        # Find publications only in CV
        for i, cv_pub in enumerate(self.cv_pubs):
            if i not in cv_matched_indices:
                self.only_in_cv.append(cv_pub)

        # Find publications only in Scholar
        for j, scholar_pub in enumerate(self.scholar_pubs):
            if j not in scholar_matched_indices:
                self.only_in_scholar.append(scholar_pub)

    def generate_report(self, output_path: str = 'output/publication_comparison.txt'):
        """Generate a comparison report."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("PUBLICATION COMPARISON REPORT\n")
            f.write("CV vs Google Scholar\n")
            f.write("=" * 80 + "\n\n")

            # Summary statistics
            f.write("SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Publications in CV: {len(self.cv_pubs)}\n")
            f.write(f"Publications in Google Scholar: {len(self.scholar_pubs)}\n")
            f.write(f"Matched: {len(self.matched)}\n")
            f.write(f"Potential matches (need review): {len(self.potential_matches)}\n")
            f.write(f"Only in CV: {len(self.only_in_cv)}\n")
            f.write(f"Only in Google Scholar: {len(self.only_in_scholar)}\n")
            f.write("\n")

            # Matched publications
            if self.matched:
                f.write("=" * 80 + "\n")
                f.write(f"MATCHED PUBLICATIONS ({len(self.matched)})\n")
                f.write("=" * 80 + "\n\n")
                for idx, match in enumerate(self.matched, 1):
                    f.write(f"{idx}. Match Score: {match['score']:.2%}\n")
                    f.write(f"   CV: {match['cv']['title']} ({match['cv']['year']})\n")
                    f.write(f"   Scholar: {match['scholar']['title']} ({match['scholar']['year']})")
                    if match['scholar'].get('citations'):
                        f.write(f" [{match['scholar']['citations']} citations]")
                    f.write("\n\n")

            # Potential matches
            if self.potential_matches:
                f.write("=" * 80 + "\n")
                f.write(f"POTENTIAL MATCHES - REVIEW NEEDED ({len(self.potential_matches)})\n")
                f.write("=" * 80 + "\n\n")
                for idx, match in enumerate(self.potential_matches, 1):
                    f.write(f"{idx}. Match Score: {match['score']:.2%}\n")
                    f.write(f"   CV: {match['cv']['title']} ({match['cv']['year']})\n")
                    f.write(f"   Scholar: {match['scholar']['title']} ({match['scholar']['year']})")
                    if match['scholar'].get('citations'):
                        f.write(f" [{match['scholar']['citations']} citations]")
                    f.write("\n\n")

            # Only in CV
            if self.only_in_cv:
                f.write("=" * 80 + "\n")
                f.write(f"ONLY IN CV - NOT FOUND IN GOOGLE SCHOLAR ({len(self.only_in_cv)})\n")
                f.write("These may need to be added to your Google Scholar profile\n")
                f.write("=" * 80 + "\n\n")
                for idx, pub in enumerate(self.only_in_cv, 1):
                    f.write(f"{idx}. {pub['title']} ({pub['year']})\n")
                    f.write(f"   Full: {pub['full_text']}\n\n")

            # Only in Scholar
            if self.only_in_scholar:
                f.write("=" * 80 + "\n")
                f.write(f"ONLY IN GOOGLE SCHOLAR - NOT FOUND IN CV ({len(self.only_in_scholar)})\n")
                f.write("These may need to be added to your CV\n")
                f.write("=" * 80 + "\n\n")
                for idx, pub in enumerate(self.only_in_scholar, 1):
                    f.write(f"{idx}. {pub['title']} ({pub['year']})\n")
                    f.write(f"   Authors: {pub['authors']}\n")
                    f.write(f"   Venue: {pub['venue']}\n")
                    if pub.get('citations'):
                        f.write(f"   Citations: {pub['citations']}\n")
                    f.write("\n")

            # Recommendations
            f.write("=" * 80 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("=" * 80 + "\n\n")

            if self.only_in_cv:
                f.write(f"1. Add {len(self.only_in_cv)} publications to Google Scholar\n")

            if self.only_in_scholar:
                f.write(f"2. Add {len(self.only_in_scholar)} publications to your CV\n")

            if self.potential_matches:
                f.write(f"3. Review {len(self.potential_matches)} potential matches - they may be the same publication\n")

            if not self.only_in_cv and not self.only_in_scholar:
                f.write("Your CV and Google Scholar profile are in sync!\n")

        print(f"\nComparison report saved to: {output_path}")
        return output_path

    def print_summary(self):
        """Print summary to console."""
        print("\n" + "=" * 60)
        print("PUBLICATION COMPARISON SUMMARY")
        print("=" * 60)
        print(f"Publications in CV: {len(self.cv_pubs)}")
        print(f"Publications in Google Scholar: {len(self.scholar_pubs)}")
        print(f"Matched: {len(self.matched)}")
        print(f"Potential matches: {len(self.potential_matches)}")
        print(f"Only in CV: {len(self.only_in_cv)}")
        print(f"Only in Google Scholar: {len(self.only_in_scholar)}")
        print("=" * 60)


def main():
    """Main function."""
    print("=" * 60)
    print("Publication Comparison Tool")
    print("=" * 60)

    comparator = PublicationComparator()

    # Extract publications from both sources
    print("\nExtracting publications from CV...")
    cv_pubs = comparator.extract_cv_publications()
    print(f"Found {len(cv_pubs)} publications in CV")

    print("\nExtracting publications from Google Scholar data...")
    scholar_pubs = comparator.extract_scholar_publications()
    print(f"Found {len(scholar_pubs)} publications in Google Scholar data")

    if not scholar_pubs:
        print("\n" + "!" * 60)
        print("WARNING: No Google Scholar publications found!")
        print("!" * 60)
        print("\nYou need to fetch Google Scholar data first.")
        print("Options:")
        print("1. Try: python scripts/fetch_scholar_simple.py 1vePPCkAAAAJ")
        print("2. Or manually copy publication data to data/publications.json")
        print("\nFor now, generating report with CV data only...")

    # Find matches
    print("\nComparing publications...")
    comparator.find_matches()

    # Generate report
    comparator.generate_report()

    # Print summary
    comparator.print_summary()

    print("\nDetailed report saved to: output/publication_comparison.txt")


if __name__ == '__main__':
    main()
