from __future__ import annotations

import csv
from pathlib import Path

from fec_formatter.cli import run_format, Args


def test_run_format_basic(tmp_path: Path):
    header = [
        "committee_name","committee_id","contributor_name","contributor_id",
        "contributor_street_1","contributor_street_2","contributor_city","contributor_state","contributor_zip",
        "contributor_employer","contributor_occupation","contribution_receipt_date","contribution_receipt_amount","image_number","pdf_url"
    ]
    rows = [
        [
            "KATIE PORTER FOR SENATE","C00831107","NAR PAC","X",
            "123 A","","SF","CA","94100","Firm","Exec","2024-01-01","100","IMG","http://x"
        ]
    ]
    src = tmp_path / "in.csv"
    with src.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

    out = tmp_path / "out.xlsx"
    args = Args(input_file=src, contributor_names=(), contributor_ids=(), output_path=out)
    setattr(args, "contributor_name_contains", ("nar",))
    run_format(args)
    assert out.exists()


