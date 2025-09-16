from __future__ import annotations

from pathlib import Path
from datetime import datetime

from fec_formatter.services import FECRowBuilder, XLSXWriterService, OUTPUT_COLUMNS
from fec_formatter.config import AppConfig


def test_row_builder_basic():
    builder = FECRowBuilder()
    header = [
        "committee_name","committee_id","contributor_name","contributor_id",
        "contributor_street_1","contributor_street_2","contributor_city","contributor_state","contributor_zip",
        "contributor_employer","contributor_occupation","contribution_receipt_date","contribution_receipt_amount","image_number","pdf_url"
    ]
    row = [
        "KATIE PORTER FOR SENATE","C00831107","WOMEN IN LEADERSHIP PAC","C00790790",
        "393 7TH AVE","STE 301","SAN FRANCISCO","CA","941182378",
        "Jones construction","CEO","2025-02-12","9790.00","202504159753351382","https://example"
    ]
    out = builder.build_row(header, row)
    assert out[0].startswith("KATIE PORTER FOR SENATE (C00831107)")
    assert out[1] == "WOMEN IN LEADERSHIP PAC (C00790790)"
    assert "SAN FRANCISCO" in out[2]
    assert out[3] == "CEO/Jones construction"
    assert out[4] == "2025-02-12"
    assert out[5] == "9790.00"
    assert out[6] == "202504159753351382"


def test_xlsx_writer_formats(tmp_path: Path):
    app = AppConfig()
    writer = XLSXWriterService(app.style)
    rows = [
        (["R","C","Addr","Occ/Emp","2025-02-12","1,000.50","IMG"], "https://example"),
    ]
    out = tmp_path / "out.xlsx"
    writer.write(rows, out)
    assert out.exists()





