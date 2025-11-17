#!/usr/bin/env python3
"""
Convenience script to update all CV data and regenerate all formats.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, shell=True)

    if result.returncode != 0:
        print(f"Error: {description} failed!")
        return False

    return True


def main():
    """Main function to update all CV data."""

    # Default values
    scholar_id = "1vePPCkAAAAJ"
    cv_path = "source_cv/cv.docx"

    # Allow overrides from command line
    if len(sys.argv) > 1:
        cv_path = sys.argv[1]
    if len(sys.argv) > 2:
        scholar_id = sys.argv[2]

    print("=" * 60)
    print("Academic CV Update All")
    print("=" * 60)
    print(f"CV Document: {cv_path}")
    print(f"Scholar ID: {scholar_id}")
    print("=" * 60)

    # Check if CV file exists
    if not Path(cv_path).exists():
        print(f"\nError: CV file not found: {cv_path}")
        print("Please place your CV Word document in the source_cv/ directory")
        print("Or specify the path: python scripts/update_all.py <cv_path> [scholar_id]")
        sys.exit(1)

    # Step 1: Parse CV
    if not run_command(
        f"python scripts/parse_cv.py {cv_path}",
        "Step 1: Parsing CV Document"
    ):
        sys.exit(1)

    # Step 2: Fetch Google Scholar data
    if not run_command(
        f"python scripts/fetch_scholar.py {scholar_id}",
        "Step 2: Fetching Google Scholar Data"
    ):
        sys.exit(1)

    # Step 3: Generate CV documents
    if not run_command(
        "python scripts/generate_cv.py",
        "Step 3: Generating CV Documents"
    ):
        sys.exit(1)

    print("\n" + "=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print("\nAll CV documents have been updated successfully!")
    print("Check the 'output/' directory for generated files:")
    print("  - academic_cv_full.docx (Full academic CV)")
    print("  - academic_cv_short.docx (Abbreviated CV)")
    print("  - publications_list.txt (Plain text publications)")
    print("=" * 60)


if __name__ == '__main__':
    main()
