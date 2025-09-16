from __future__ import annotations

from pathlib import Path
import csv
import pytest

from fec_formatter.combiner import CSVCombinerService, CSVCombineError


def _write_csv(path: Path, header: list[str], rows: list[list[str]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def test_combiner_happy_path(tmp_path: Path):
    header = ["a", "b"]
    _write_csv(tmp_path / "one.csv", header, [["1", "2"], ["3", "4"]])
    _write_csv(tmp_path / "two.csv", header, [["5", "6"]])

    out = tmp_path / "combined.csv"
    result = CSVCombinerService().combine(tmp_path, out)

    assert result.files_combined == 2
    assert result.rows_written == 3
    assert result.header_columns == 2
    assert out.exists()


def test_combiner_mismatched_header_raises(tmp_path: Path):
    _write_csv(tmp_path / "one.csv", ["a", "b"], [["1", "2"]])
    _write_csv(tmp_path / "two.csv", ["x", "y"], [["3", "4"]])
    with pytest.raises(CSVCombineError):
        CSVCombinerService().combine(tmp_path, tmp_path / "combined.csv")


