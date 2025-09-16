from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional


@dataclass(frozen=True)
class CombineResult:
    files_combined: int
    rows_written: int
    header_columns: int
    output_path: Path


class CSVCombineError(Exception):
    pass


class CSVCombinerService:
    def combine(
        self,
        input_dir: Path,
        output_path: Path,
        pattern: str = "*.csv",
        overwrite: bool = False,
    ) -> CombineResult:
        input_dir = input_dir.resolve()
        if not input_dir.exists() or not input_dir.is_dir():
            raise CSVCombineError(f"Input directory not found or not a directory: {input_dir}")

        files = sorted(input_dir.glob(pattern))
        if not files:
            raise CSVCombineError(f"No CSV files found in {input_dir} matching '{pattern}'")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists() and not overwrite:
            raise CSVCombineError(
                f"Output file already exists: {output_path}. Use --overwrite to replace it."
            )

        first_header: Optional[List[str]] = None
        files_combined = 0
        rows_written = 0

        temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
        try:
            with temp_path.open("w", encoding="utf-8", newline="") as out_f:
                writer = csv.writer(out_f)
                for csv_path in files:
                    header = self._read_header(csv_path)
                    if first_header is None:
                        first_header = header
                        writer.writerow(first_header)
                    else:
                        if header != first_header:
                            raise CSVCombineError(
                                "Header mismatch detected between files; refusing to combine"
                            )

                    for row in self._iter_rows_excluding_header(csv_path):
                        writer.writerow(row)
                        rows_written += 1
                    files_combined += 1
            os.replace(temp_path, output_path)
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass

        return CombineResult(
            files_combined=files_combined,
            rows_written=rows_written,
            header_columns=len(first_header or []),
            output_path=output_path,
        )

    def _read_header(self, file_path: Path) -> List[str]:
        with file_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                raise CSVCombineError(f"File is empty (no header): {file_path}")
            if not header:
                raise CSVCombineError(f"Header row is empty in file: {file_path}")
            return header

    def _iter_rows_excluding_header(self, file_path: Path) -> Iterator[List[str]]:
        with file_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            try:
                next(reader)
            except StopIteration:
                return
            for row in reader:
                if not row or all(cell == "" for cell in row):
                    continue
                yield row



