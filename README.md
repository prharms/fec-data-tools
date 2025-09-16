FEC Data Tools
==============

Overview
--------
This repository provides utilities for working with Federal Elections Commission (FEC) CSV exports via a unified CLI:

- `fec_formatter/`: Package and CLI to combine CSVs and convert a single FEC CSV into a styled XLSX per specification.

Installation
------------
Requires Python 3.11+.

Install with pyproject (recommended):

```bash
pip install -e .
```

Key dependency: `openpyxl` (installed via pyproject) for XLSX writing.

Usage
-----
Combine CSVs:

```bash
python -m fec_formatter.cli combine --input-dir data --output output/combined.csv
```

Format to XLSX:

```bash
python -m fec_formatter.cli format-xlsx --input-file "data/01 - C00831107 (Sen) - 2025-2026.csv" --output output/fec_formatted.xlsx
```

Filtering options:

- `--contributor-name` can be provided multiple times for exact matches (case-insensitive, whitespace-normalized). OR logic across values.
- `--contributor-name-contains` can be provided multiple times for substring matches (case-insensitive). OR logic across values.

Example with both exact and contains filters:

```bash
fec-tools format-xlsx \
  --input-file "output/combined.csv" \
  --output "output/filtered.xlsx" \
  --contributor-name "National Association of Realtors Political Action Committee" \
  --contributor-name-contains "apartment association" \
  --contributor-name-contains "realtors"
```

XLSX Output Spec
----------------
- Columns: Recipient, Contributor, Contributor Address, Contributor Occupation/Employer, Contribution Date, Contribution Amount, FEC ID
- Recipient: `committee_name (committee_id)`
- Contributor: `contributor_name` with ` (contributor_id)` appended if present and not `C00401224`
- Address: `contributor_street_1, contributor_street_2, contributor_city, contributor_state contributor_zip`
- Occupation/Employer: `contributor_occupation/contributor_employer` if present
- Date: from `contribution_receipt_date` (formatted `M/D/YYYY`)
- Amount: from `contribution_receipt_amount` (currency)
- FEC ID: from `image_number`, hyperlinked to `pdf_url` when available

Styling
-------
- Base font: Garamond 9pt
- Header: bold, medium gray fill
- Hyperlinks: underlined, blue
- Borders: thin borders for all cells

Architecture
------------
- Composition root: `fec_formatter/container.py` constructs services with `AppConfig`
- Configuration: `fec_formatter/config.py` centralizes style configuration
- Services:
  - `FECRowBuilder`: builds output rows and applies filtering logic
  - `XLSXWriterService`: renders rows to XLSX with styling and number formats
- CLI: `fec_formatter/cli.py` provides subcommands (`combine`, `format-xlsx`) and wires services via the container

Testing
-------
Run tests:

```bash
python -m pytest -q
```

License
-------
MIT


