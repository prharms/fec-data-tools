from __future__ import annotations

import csv
from pathlib import Path
import subprocess, sys


def test_cli_format_subcommand(tmp_path: Path):
    header = [
        "committee_name","committee_id","contributor_name","contributor_id",
        "contributor_street_1","contributor_street_2","contributor_city","contributor_state","contributor_zip",
        "contributor_employer","contributor_occupation","contribution_receipt_date","contribution_receipt_amount","image_number","pdf_url"
    ]
    rows = [["A","X","B","","s1","","c","CA","9","e","o","2024-01-01","10","IMG","http://x"]]
    src = tmp_path / "in.csv"
    with src.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    out = tmp_path / "out.xlsx"
    cmd = [sys.executable, "-m", "fec_formatter.cli", "format-xlsx", "--input-file", str(src), "--output", str(out)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    assert out.exists()


def test_cli_combine_subcommand(tmp_path: Path):
    d = tmp_path / "d"; d.mkdir()
    with (d / "a.csv").open("w", encoding="utf-8", newline="") as f:
        f.write("h1,h2\n1,2\n")
    with (d / "b.csv").open("w", encoding="utf-8", newline="") as f:
        f.write("h1,h2\n3,4\n")
    out = tmp_path / "c.csv"
    cmd = [sys.executable, "-m", "fec_formatter.cli", "combine", "--input-dir", str(d), "--output", str(out)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    assert out.exists()

