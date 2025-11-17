# Publication Comparison Guide

This guide explains how to compare publications between your CV and Google Scholar to identify gaps and discrepancies.

## Why Compare?

Comparing your CV against Google Scholar helps you:

1. **Find publications missing from Google Scholar** - Ensure all your work is indexed
2. **Find publications missing from your CV** - Keep your CV up-to-date
3. **Identify discrepancies** - Catch formatting differences or duplicates
4. **Track citation counts** - See which publications are being cited

## Quick Start

### Option 1: With Google Scholar API Access (if it works)

If you can access Google Scholar programmatically:

```bash
# Step 1: Fetch Google Scholar data
python scripts/fetch_scholar_simple.py 1vePPCkAAAAJ

# Step 2: Run comparison
python scripts/compare_publications.py
```

Check `output/publication_comparison.txt` for the detailed report.

### Option 2: Manual Import (Recommended)

Since Google Scholar blocks automated access, use manual import:

#### Step 1: Export from Google Scholar

1. Go to your [Google Scholar profile](https://scholar.google.com/citations?user=1vePPCkAAAAJ&hl=en)
2. Click "Export" and select "BibTeX" or "CSV" (if available)
3. Or simply copy your publication list to a text file

Example text format (`scholar_pubs.txt`):
```
Infrastructuring heterogeneity: Design for decentered displacement
R Soden, N Palen
Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems
Cited by 15

Modes of uncertainty: Rethinking flood risk in Colorado
R Soden, L Palen
Big Data & Society 5 (1)
Cited by 42
```

#### Step 2: Import the Data

```bash
python scripts/import_scholar_manual.py scholar_pubs.txt
```

You'll be prompted to enter:
- Your name
- Affiliation
- Total citations
- h-index
- i10-index
- Profile URL

#### Step 3: Run Comparison

```bash
python scripts/compare_publications.py
```

## Understanding the Report

The comparison report (`output/publication_comparison.txt`) contains:

### 1. Summary Statistics

```
Publications in CV: 108
Publications in Google Scholar: 45
Matched: 38
Potential matches: 3
Only in CV: 67
Only in Google Scholar: 4
```

### 2. Matched Publications

Publications found in both sources with high confidence (>85% similarity):

```
1. Match Score: 95%
   CV: Infrastructuring heterogeneity (2023)
   Scholar: Infrastructuring heterogeneity: Design for decentered displacement (2023) [15 citations]
```

### 3. Potential Matches (Review Needed)

Publications that might be the same but need manual review (65-85% similarity):

```
1. Match Score: 72%
   CV: Crisis Informatics in the Anthropocene (2019)
   Scholar: Disasters as Matters of Care (2019) [25 citations]
```

These might be:
- Same publication with different title formatting
- Related works (e.g., dissertation vs. paper)
- False positives

### 4. Only in CV

Publications in your CV but not found in Google Scholar:

```
1. Monitoring, Evaluation, Reporting, and Learning for Climate Resilience (2025)
```

**Action**: Consider adding these to your Google Scholar profile

**Why they might be missing**:
- Too recent (not yet indexed)
- Grey literature (technical reports, white papers)
- Not digitally available
- Different title in Google Scholar

### 5. Only in Google Scholar

Publications in Google Scholar but not in your CV:

```
1. Short paper title (2020)
   Authors: Soden, R., Collaborator, A.
   Venue: Minor Conference
   Citations: 2
```

**Action**: Consider adding these to your CV (especially if highly cited)

**Why they might be missing**:
- Forgotten older work
- Workshop papers you didn't include
- Co-authored papers where you're not first author

## Workflow for Syncing

### 1. Review Potential Matches

For each potential match, manually check if they're the same publication:

```python
# Edit data/publications.json
# Update title to match CV format if they're the same publication
```

### 2. Add Missing Publications to CV

For publications only in Google Scholar:

1. Check if they should be in your CV
2. Add high-citation papers first
3. Update your CV Word document
4. Re-run `python scripts/parse_cv.py source_cv/cv.docx`

### 3. Add Missing Publications to Google Scholar

For publications only in CV:

1. Visit your [Google Scholar profile](https://scholar.google.com/citations?user=1vePPCkAAAAJ&hl=en)
2. Click "Add" → "Add article manually"
3. Enter publication details
4. Re-run the comparison after a few days

### 4. Update Citation Counts

Once matched, update citation counts in your CV:

```bash
# Regenerate CV with updated citations
python scripts/generate_cv.py
```

## Advanced: Customizing Comparison

Edit `scripts/compare_publications.py` to adjust:

### Similarity Thresholds

```python
comparator.find_matches(
    threshold=0.85,           # Definite match threshold
    potential_threshold=0.65  # Potential match threshold
)
```

- Higher threshold = fewer false positives, more unmatched
- Lower threshold = more matches, more false positives

### Normalize Title Function

Customize how titles are compared:

```python
def normalize_title(self, title: str) -> str:
    # Add custom normalization rules
    title = title.replace('&', 'and')
    # Remove common suffixes
    title = re.sub(r'\s*\(extended abstract\)', '', title)
    return title
```

## Tips for Maintaining Sync

1. **Regular updates**: Run comparison quarterly
2. **Track changes**: Keep a log of added/removed publications
3. **Citation monitoring**: Update citation counts before job applications
4. **Grey literature**: Some reports may never appear in Google Scholar
5. **Formatting consistency**: Use consistent title formatting in both sources

## Troubleshooting

### "No Google Scholar publications found"

- You haven't imported Google Scholar data yet
- Run `python scripts/import_scholar_manual.py` first

### "Too many false matches"

- Increase the threshold in `compare_publications.py`
- Improve title normalization

### "Publications not matching that should"

- Check title formatting differences
- Verify years match
- Lower the similarity threshold

## Example Complete Workflow

```bash
# 1. Parse your CV
python scripts/parse_cv.py source_cv/cv.docx

# 2. Copy Google Scholar publications to scholar_pubs.txt
# (Visit your profile and copy publication list)

# 3. Import Google Scholar data
python scripts/import_scholar_manual.py scholar_pubs.txt

# 4. Run comparison
python scripts/compare_publications.py

# 5. Review the report
cat output/publication_comparison.txt

# 6. Make updates to CV or Google Scholar as needed

# 7. Regenerate CVs with updated data
python scripts/generate_cv.py
```

## Next Steps

After comparing and syncing:

1. Update `data/publications.json` with accurate citation counts
2. Regenerate your CVs with `python scripts/generate_cv.py`
3. Set a calendar reminder to re-run comparison every 3-6 months
4. Keep a backup of your `data/publications.json` file

---

For questions or issues, check the main [README.md](README.md) or the script source code.
