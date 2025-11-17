# Incremental Update Guide

This guide explains how to maintain your publication database over time by only adding new publications, rather than re-importing everything.

## Why Incremental Updates?

- **Save time**: Only process new publications
- **Avoid duplicates**: Automatically detects existing publications
- **Preserve manual edits**: Keep any customizations you've made
- **Automatic backups**: Creates timestamped backups before merging

## Quick Workflow

### First Time Setup

```bash
# 1. Parse your CV
python scripts/parse_cv.py source_cv/cv.docx

# 2. Import all your publications from Google Scholar
python scripts/import_scholar_manual.py scholar_all.txt

# 3. Generate your CV
python scripts/generate_cv.py
```

### Periodic Updates (Monthly/Quarterly)

```bash
# 1. Copy ONLY your recent publications from Google Scholar to a file
# (Just the new ones from the last few months)

# 2. Import in incremental mode
python scripts/import_scholar_manual.py scholar_new.txt --incremental

# 3. Merge new publications
python scripts/update_incremental.py data/publications_new.json

# 4. Regenerate your CV
python scripts/generate_cv.py
```

## Detailed Walkthrough

### Step 1: Get New Publications

Visit your Google Scholar profile and copy only recent publications:

```
My New Paper About Climate
Soden, R., Collaborator, A.
CHI 2025
Cited by 5

Another Recent Publication
Soden, R.
CSCW 2025
Cited by 2
```

Save this to a file (e.g., `scholar_new_2025.txt`)

### Step 2: Import with --incremental Flag

```bash
python scripts/import_scholar_manual.py scholar_new_2025.txt --incremental
```

This will:
- Parse the publications
- Save to `data/publications_new.json` (separate from your main database)
- Skip author info prompts (preserves your existing data)

### Step 3: Run Incremental Merge

```bash
python scripts/update_incremental.py data/publications_new.json
```

The script will:
1. **Compare** new publications against existing database
2. **Identify**:
   - Truly new publications
   - Duplicates (>85% similarity)
   - Potential duplicates (65-85% similarity)
3. **Show you a report**:
   ```
   Existing publications: 108
   New data contains: 12 publications

   Truly new: 8
   Duplicates (skipped): 3
   Potential duplicates (review needed): 1
   ```
4. **Ask for confirmation** before merging
5. **Create a backup** of your existing data
6. **Merge** only the truly new publications

### Step 4: Review Potential Duplicates

If there are potential duplicates (65-85% similarity), the script will show them:

```
POTENTIAL DUPLICATES - REVIEW NEEDED (1)

1. Similarity: 72%
   NEW: Climate Observatory Development (2025)
   EXISTING: Towards a Public Climate Observatory (2025)
```

These might be:
- Same paper with slightly different title
- Related papers (conference vs journal version)
- False positives

**Options:**
- Type `y` to merge anyway (you can manually remove duplicates later)
- Type `n` to cancel and manually edit `data/publications_new.json` first

### Step 5: Regenerate CV

```bash
python scripts/generate_cv.py
```

Your CV now includes the new publications!

## Advanced Options

### Similarity Thresholds

Edit `scripts/update_incremental.py` to adjust matching:

```python
updater.find_new_publications(similarity_threshold=0.85)
```

- Higher (e.g., 0.90): More strict, fewer false duplicates, might miss some matches
- Lower (e.g., 0.80): More lenient, catches more duplicates, might have false positives

### Manual Review Before Merge

Instead of automatic merge, review the new publications first:

```bash
# 1. Import incrementally
python scripts/import_scholar_manual.py scholar_new.txt --incremental

# 2. Review what was imported
cat data/publications_new.json

# 3. Manually edit if needed
nano data/publications_new.json

# 4. Merge
python scripts/update_incremental.py data/publications_new.json
```

### Restore from Backup

If a merge goes wrong:

```bash
# Backups are saved as: data/publications.json.backup.YYYYMMDD_HHMMSS
# Find your backup
ls -lt data/publications.json.backup.*

# Restore it
cp data/publications.json.backup.20250117_143022 data/publications.json
```

## Citation Counts

By default, citation counts are **NOT shown** in the generated CVs. This is intentional because:
- Citation counts change frequently
- They can make CVs look cluttered
- Focus is on the work itself, not metrics

If you want to include citations:

```bash
python scripts/generate_cv.py --include-citations
```

## Best Practices

### 1. Regular Schedule

Set a recurring reminder to update your publications:
- **Monthly**: If you publish frequently
- **Quarterly**: For most academics
- **Before job applications**: Always update before applying

### 2. Track Your Updates

Keep a log of when you update:

```bash
echo "$(date): Added 5 new publications" >> publication_updates.log
```

### 3. Separate Files for Each Update

Don't reuse the same file:

```bash
scholar_new_jan2025.txt
scholar_new_apr2025.txt
scholar_new_jul2025.txt
```

This helps track what was added when.

### 4. Version Control

Commit your `data/publications.json` after each update:

```bash
git add data/publications.json
git commit -m "Add 5 new publications from Q1 2025"
```

### 5. Verify After Merge

Always check the results:

```bash
# How many publications now?
python -c "import json; print(len(json.load(open('data/publications.json'))['publications']))"

# Regenerate and review
python scripts/generate_cv.py
cat output/publications_list.txt | head -20
```

## Troubleshooting

### "All publications marked as duplicates"

You may have re-imported the same file. Make sure you're importing only NEW publications.

### "Similarity too low, missing matches"

Some publications have very different titles in Google Scholar vs your CV. You can:
1. Manually add them to `data/publications.json`
2. Lower the similarity threshold

### "Too many potential duplicates"

This is normal if you have many similar paper titles. Review them manually:

```bash
# Don't merge automatically
# Answer 'n' when prompted
# Then manually check data/publications_new.json
# Remove obvious duplicates
# Re-run the merge
```

## Example: Complete Update Workflow

```bash
# === January 2025 Update ===

# 1. Visit Google Scholar, copy 3 new publications
# Save to scholar_jan2025.txt

# 2. Import
python scripts/import_scholar_manual.py scholar_jan2025.txt --incremental

# Output:
# Found 3 publications
# Incremental mode: Skipping author info
# Data saved to: data/publications_new.json

# 3. Merge
python scripts/update_incremental.py data/publications_new.json

# Output:
# Existing publications: 108
# New data contains: 3 publications
# Truly new: 3
# Duplicates: 0
# Ready to add 3 new publications
# Merge? (Y/n): y
# Created backup: data/publications.json.backup.20250117_150322
# Merged data saved to: data/publications.json

# 4. Regenerate CV
python scripts/generate_cv.py

# 5. Review
cat output/publications_list.txt | head -15

# 6. Commit
git add data/publications.json
git commit -m "Added 3 publications from January 2025"
```

## Integration with Comparison Tool

After updating, you can compare against your CV:

```bash
# Update publications from Google Scholar
python scripts/update_incremental.py data/publications_new.json

# Compare with your CV
python scripts/compare_publications.py

# This will show if your CV is missing any publications
```

## Summary

**Incremental updates save you time and prevent errors:**

✅ Only process new publications
✅ Automatic duplicate detection
✅ Preserve manual edits
✅ Create backups
✅ No citation clutter by default

**Workflow:**
1. Copy recent pubs → `scholar_new.txt`
2. `python scripts/import_scholar_manual.py scholar_new.txt --incremental`
3. `python scripts/update_incremental.py data/publications_new.json`
4. `python scripts/generate_cv.py`

---

See [README.md](README.md) for general usage and [COMPARISON_GUIDE.md](COMPARISON_GUIDE.md) for comparing CV vs Google Scholar.
