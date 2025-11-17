# Academic CV Management Scripts

A collection of Python scripts to help manage your academic CV by parsing existing Word documents, pulling live updates from Google Scholar, and generating CVs in multiple formats.

## Features

- **Parse existing CV**: Extract structured data from Word document CVs
- **Google Scholar integration**: Automatically fetch publications, citations, and metrics
- **Multiple output formats**: Generate full CV, short CV, and publication lists
- **Up-to-date metrics**: Include current citation counts, h-index, and i10-index
- **Automated workflow**: Single command to update everything

## Project Structure

```
cv/
├── scripts/
│   ├── parse_cv.py          # Parse Word document CV
│   ├── fetch_scholar.py     # Fetch Google Scholar data
│   ├── generate_cv.py       # Generate CV documents
│   └── update_all.py        # Update everything at once
├── source_cv/               # Place your original CV here
├── templates/               # CV templates (future)
├── data/                    # Extracted data (JSON)
├── output/                  # Generated CV documents
├── requirements.txt         # Python dependencies
└── README.md
```

## Installation

1. **Clone the repository** (or you already have it)

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - `python-docx`: Parse and create Word documents
   - `scholarly`: Fetch Google Scholar data
   - `jinja2`: Template engine (for future enhancements)
   - Other supporting libraries

## Quick Start

### Option 1: Update Everything at Once (Recommended)

1. **Place your CV** in the `source_cv/` directory:
   ```bash
   cp /path/to/your/cv.docx source_cv/cv.docx
   ```

2. **Run the update script**:
   ```bash
   python scripts/update_all.py
   ```

   This will:
   - Parse your CV from the Word document
   - Fetch your latest publications from Google Scholar
   - Generate all CV formats

3. **Check the output** in the `output/` directory:
   - `academic_cv_full.docx` - Full academic CV with all publications
   - `academic_cv_short.docx` - Abbreviated CV with top 10 publications
   - `publications_list.txt` - Plain text list of all publications

### Option 2: Step-by-Step

If you want more control, run each script individually:

#### Step 1: Parse Your CV
```bash
python scripts/parse_cv.py source_cv/cv.docx
```

This extracts structured data from your Word document and saves it to `data/cv_data.json`.

#### Step 2: Fetch Google Scholar Data
```bash
python scripts/fetch_scholar.py 1vePPCkAAAAJ
```

Replace `1vePPCkAAAAJ` with your Google Scholar user ID.

To find your Scholar ID:
1. Go to your Google Scholar profile
2. Look at the URL: `https://scholar.google.com/citations?user=YOUR_ID_HERE`

This fetches your publications and saves them to `data/publications.json`.

#### Step 3: Generate CV Documents
```bash
python scripts/generate_cv.py
```

This creates all CV formats in the `output/` directory.

## Detailed Usage

### parse_cv.py

Parse a Word document CV and extract structured data.

```bash
python scripts/parse_cv.py <path_to_cv.docx>
```

**What it does**:
- Extracts personal information (name, email, phone)
- Identifies sections (education, experience, publications, awards)
- Parses tables and paragraphs
- Saves structured data to `data/cv_data.json`

**Example**:
```bash
python scripts/parse_cv.py source_cv/my_cv.docx
```

### fetch_scholar.py

Fetch publication data from Google Scholar.

```bash
python scripts/fetch_scholar.py <scholar_id> [max_publications]
```

**Arguments**:
- `scholar_id`: Your Google Scholar user ID (required)
- `max_publications`: Maximum number of publications to fetch (optional, default: all)

**What it does**:
- Fetches author information (name, affiliation, interests)
- Retrieves all publications with details
- Gets citation metrics (h-index, i10-index, total citations)
- Saves data to `data/publications.json`

**Example**:
```bash
# Fetch all publications
python scripts/fetch_scholar.py 1vePPCkAAAAJ

# Fetch only the first 20 publications (faster)
python scripts/fetch_scholar.py 1vePPCkAAAAJ 20
```

**Note**: Google Scholar may rate-limit requests. If you have many publications, consider:
- Fetching a limited number first to test
- Adding delays between requests (already built-in)
- Using a proxy (uncomment in the code)

### generate_cv.py

Generate CV documents from the extracted data.

```bash
python scripts/generate_cv.py
```

**What it generates**:
- `output/academic_cv_full.docx`: Complete CV with all publications, sorted by year
- `output/academic_cv_short.docx`: Abbreviated CV with top 10 most-cited publications
- `output/publications_list.txt`: Plain text list of publications

**Features**:
- Includes Google Scholar metrics (citations, h-index, i10-index)
- Shows citation counts for each publication
- Professional formatting
- Automatically sorted publications

### update_all.py

Convenience script to update everything in one command.

```bash
python scripts/update_all.py [cv_path] [scholar_id]
```

**Arguments** (all optional):
- `cv_path`: Path to your CV (default: `source_cv/cv.docx`)
- `scholar_id`: Your Google Scholar ID (default: `1vePPCkAAAAJ`)

**Example**:
```bash
# Use defaults
python scripts/update_all.py

# Specify custom paths
python scripts/update_all.py source_cv/my_cv.docx ABC123XYZ
```

## Configuration

### Update Your Scholar ID

Edit `scripts/update_all.py` and change the default Scholar ID:

```python
scholar_id = "YOUR_SCHOLAR_ID_HERE"
```

### Customize Output Formats

Edit `scripts/generate_cv.py` to customize:
- Number of publications in short CV
- Formatting styles
- Section order
- Citation formats

## Data Files

### data/cv_data.json

Contains parsed data from your Word document:
```json
{
  "personal_info": {
    "name": "Your Name",
    "email": "your.email@example.com"
  },
  "other_sections": {
    "education": [...],
    "experience": [...],
    "awards": [...]
  },
  "all_paragraphs": [...],
  "tables": [...]
}
```

### data/publications.json

Contains Google Scholar data:
```json
{
  "author_info": {
    "name": "Your Name",
    "affiliation": "Your Institution",
    "citedby": 1234,
    "hindex": 20,
    "i10index": 35
  },
  "publications": [
    {
      "title": "Paper Title",
      "authors": "Author List",
      "year": "2024",
      "venue": "Conference/Journal",
      "citations": 42
    }
  ]
}
```

## Tips and Best Practices

1. **Keep your source CV updated**: The scripts work best with a well-structured Word document

2. **Regular updates**: Run `update_all.py` periodically to keep your CV current with latest citations

3. **Version control**: Commit your scripts but keep your actual CV files private (see `.gitignore`)

4. **Customize templates**: Modify `generate_cv.py` to match your institution's CV format requirements

5. **Check the data files**: Review `data/*.json` files to ensure parsing worked correctly

6. **Google Scholar limits**: If fetching fails, try reducing the number of publications or add delays

## Troubleshooting

### "File not found" error
- Make sure your CV is in the `source_cv/` directory
- Check that the filename matches what you're passing to the script

### Google Scholar errors
- Google may rate-limit requests
- Try fetching fewer publications first
- Wait a few minutes between runs
- Consider enabling proxy in `fetch_scholar.py`

### Missing data in generated CVs
- Check `data/cv_data.json` to see what was parsed from your CV
- Your original CV may need better structure (clear section headers)
- You can manually edit the JSON files if needed

### Python dependencies not found
```bash
pip install -r requirements.txt
```

## Future Enhancements

Potential improvements:
- [ ] LaTeX template support
- [ ] HTML/web CV generation
- [ ] Custom Jinja2 templates
- [ ] Integration with ORCID
- [ ] PDF generation
- [ ] Automatic deployment to personal website
- [ ] Citation graph visualization
- [ ] Multiple citation format styles (APA, MLA, Chicago)

## License

This project is provided as-is for academic use.

## Contributing

Feel free to submit issues or pull requests to improve the scripts!

---

**Your Google Scholar Profile**: https://scholar.google.com/citations?user=1vePPCkAAAAJ&hl=en
