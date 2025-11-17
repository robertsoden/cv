#!/usr/bin/env python3
"""
Incremental publication updater - only import new publications.

This script compares your current publication data with new data
and only adds publications that don't already exist.
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
from difflib import SequenceMatcher


class IncrementalUpdater:
    """Manage incremental updates to publication data."""

    def __init__(self,
                 existing_data_path: str = 'data/publications.json',
                 new_data_path: str = 'data/publications_new.json'):
        """
        Initialize the updater.

        Args:
            existing_data_path: Path to current publications.json
            new_data_path: Path to newly imported data
        """
        self.existing_path = Path(existing_data_path)
        self.new_path = Path(new_data_path)

        self.existing_data = self._load_json(self.existing_path)
        self.new_data = self._load_json(self.new_path)

        self.existing_pubs = self.existing_data.get('publications', [])
        self.new_pubs = self.new_data.get('publications', [])

        self.truly_new = []
        self.duplicates = []
        self.potential_duplicates = []

    def _load_json(self, path: Path) -> Dict:
        """Load JSON data from file."""
        if not path.exists():
            return {}

        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def normalize_title(self, title: str) -> str:
        """Normalize title for comparison."""
        import re
        title = title.lower()
        title = re.sub(r'[.,;:!?"\']', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        return title

    def similarity_score(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, str1, str2).ratio()

    def find_new_publications(self, similarity_threshold: float = 0.85):
        """
        Identify truly new publications.

        Args:
            similarity_threshold: Threshold for considering publications the same
        """
        for new_pub in self.new_pubs:
            new_title_norm = self.normalize_title(new_pub.get('title', ''))
            new_year = str(new_pub.get('year', ''))

            is_duplicate = False
            best_match = None
            best_score = 0

            # Check against all existing publications
            for existing_pub in self.existing_pubs:
                existing_title_norm = self.normalize_title(existing_pub.get('title', ''))
                existing_year = str(existing_pub.get('year', ''))

                # Calculate similarity
                score = self.similarity_score(new_title_norm, existing_title_norm)

                # Penalize year mismatch
                if new_year and existing_year and new_year != existing_year:
                    score *= 0.7

                if score > best_score:
                    best_score = score
                    best_match = existing_pub

                # Definite duplicate
                if score >= similarity_threshold:
                    is_duplicate = True
                    self.duplicates.append({
                        'new': new_pub,
                        'existing': existing_pub,
                        'score': score
                    })
                    break

            # Not a duplicate but somewhat similar
            if not is_duplicate:
                if best_score >= 0.65:  # Potential duplicate
                    self.potential_duplicates.append({
                        'new': new_pub,
                        'existing': best_match,
                        'score': best_score
                    })
                else:  # Truly new
                    self.truly_new.append(new_pub)

    def merge_and_save(self, output_path: str = 'data/publications.json',
                       backup: bool = True):
        """
        Merge new publications into existing data and save.

        Args:
            output_path: Where to save merged data
            backup: Whether to create backup of existing file
        """
        if backup and self.existing_path.exists():
            backup_path = Path(f"{output_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            import shutil
            shutil.copy(self.existing_path, backup_path)
            print(f"Created backup: {backup_path}")

        # Start with existing data
        merged_data = self.existing_data.copy()

        # Update author info with latest from new data (if provided)
        if self.new_data.get('author_info'):
            merged_data['author_info'] = self.new_data['author_info']

        # Add truly new publications
        all_pubs = self.existing_pubs + self.truly_new

        # Sort by year (descending)
        all_pubs.sort(key=lambda x: int(x.get('year', 0) or 0), reverse=True)

        merged_data['publications'] = all_pubs
        merged_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        merged_data['total_publications'] = len(all_pubs)

        # Save merged data
        output_path = Path(output_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)

        print(f"\nMerged data saved to: {output_path}")

    def generate_report(self):
        """Generate a report of what was found."""
        print("\n" + "=" * 70)
        print("INCREMENTAL UPDATE REPORT")
        print("=" * 70)
        print(f"\nExisting publications: {len(self.existing_pubs)}")
        print(f"New data contains: {len(self.new_pubs)} publications")
        print(f"\nTruly new: {len(self.truly_new)}")
        print(f"Duplicates (skipped): {len(self.duplicates)}")
        print(f"Potential duplicates (review needed): {len(self.potential_duplicates)}")

        if self.truly_new:
            print("\n" + "-" * 70)
            print(f"TRULY NEW PUBLICATIONS ({len(self.truly_new)})")
            print("-" * 70)
            for idx, pub in enumerate(self.truly_new, 1):
                print(f"{idx}. {pub.get('title', 'Unknown')} ({pub.get('year', 'N/A')})")

        if self.potential_duplicates:
            print("\n" + "-" * 70)
            print(f"POTENTIAL DUPLICATES - REVIEW NEEDED ({len(self.potential_duplicates)})")
            print("-" * 70)
            for idx, match in enumerate(self.potential_duplicates, 1):
                print(f"\n{idx}. Similarity: {match['score']:.2%}")
                print(f"   NEW: {match['new'].get('title', '')} ({match['new'].get('year', '')})")
                print(f"   EXISTING: {match['existing'].get('title', '')} ({match['existing'].get('year', '')})")

        if self.duplicates:
            print("\n" + "-" * 70)
            print(f"DUPLICATES SKIPPED ({len(self.duplicates)})")
            print("-" * 70)
            for idx, match in enumerate(self.duplicates[:5], 1):  # Show first 5
                print(f"{idx}. {match['new'].get('title', '')} (already exists)")
            if len(self.duplicates) > 5:
                print(f"   ... and {len(self.duplicates) - 5} more")


def main():
    """Main function."""
    import sys

    print("=" * 70)
    print("Incremental Publication Updater")
    print("=" * 70)

    if len(sys.argv) < 2:
        print("\nUsage: python scripts/update_incremental.py <new_data_file>")
        print("\nExample workflow:")
        print("1. Import new Scholar data:")
        print("   python scripts/import_scholar_manual.py scholar_new.txt")
        print("   (This creates data/publications_new.json)")
        print("")
        print("2. Merge incrementally:")
        print("   python scripts/update_incremental.py data/publications_new.json")
        print("")
        print("Or specify custom paths:")
        print("   python scripts/update_incremental.py new_data.json existing_data.json")
        sys.exit(0)

    new_data_path = sys.argv[1]
    existing_data_path = 'data/publications.json'

    if len(sys.argv) > 2:
        existing_data_path = sys.argv[2]

    # Check if files exist
    if not Path(new_data_path).exists():
        print(f"Error: New data file not found: {new_data_path}")
        sys.exit(1)

    if not Path(existing_data_path).exists():
        print(f"Warning: Existing data file not found: {existing_data_path}")
        print("Will create new file with all publications from new data.")
        # Just copy the new file
        import shutil
        shutil.copy(new_data_path, existing_data_path)
        print(f"Created: {existing_data_path}")
        sys.exit(0)

    # Run the update
    updater = IncrementalUpdater(existing_data_path, new_data_path)

    print("\nAnalyzing publications...")
    updater.find_new_publications()

    # Generate report
    updater.generate_report()

    # Ask for confirmation if there are new publications
    if updater.truly_new or updater.potential_duplicates:
        print("\n" + "=" * 70)

        if updater.potential_duplicates:
            print("\nWARNING: There are potential duplicates that need review.")
            print("You should check these manually before merging.")
            print("\nDo you want to merge anyway? (y/N): ", end='')
        else:
            print(f"\nReady to add {len(updater.truly_new)} new publications.")
            print("Merge these into your publication data? (Y/n): ", end='')

        response = input().strip().lower()

        if updater.potential_duplicates:
            should_merge = response == 'y'
        else:
            should_merge = response != 'n'

        if should_merge:
            updater.merge_and_save()
            print("\n✓ Publications merged successfully!")
            print(f"  Total publications: {len(updater.existing_pubs) + len(updater.truly_new)}")
            print(f"  New publications added: {len(updater.truly_new)}")
        else:
            print("\nMerge cancelled. No changes made.")
    else:
        print("\n✓ No new publications to add. Database is up to date!")


if __name__ == '__main__':
    main()
