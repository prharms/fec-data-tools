from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple
from functools import cmp_to_key
from datetime import datetime

from .container import Container
from .services import FECRowBuilder, XLSXWriterService
from .combiner import CSVCombinerService


from .services import OUTPUT_COLUMNS, _parse_date


@dataclass
class Args:
    input_file: Path
    contributor_names: Sequence[str]
    contributor_ids: Sequence[str]
    output_path: Path


def parse_args(argv: Optional[Sequence[str]] = None) -> Args:
    parser = argparse.ArgumentParser(description="FEC Data Tools")
    sub = parser.add_subparsers(dest="command", required=True)

    # format-xlsx
    p_fmt = sub.add_parser("format-xlsx", help="Format a FEC CSV into styled XLSX")
    p_fmt.add_argument("--input-file", type=Path, required=True, help="Source FEC CSV file")
    p_fmt.add_argument(
        "--contributor-name",
        dest="contributor_names",
        action="append",
        default=[],
        help="Exact contributor_name to include (can be passed multiple times; OR logic)",
    )
    p_fmt.add_argument(
        "--contributor-name-contains",
        dest="contributor_name_contains",
        action="append",
        default=[],
        help="Substring match (case-insensitive) for contributor_name; can be used multiple times (OR logic)",
    )
    # Accept misspelling alias from SPEC.md
    p_fmt.add_argument(
        "--contrbutor-name",
        dest="contributor_names",
        action="append",
        help=argparse.SUPPRESS,
    )
    p_fmt.add_argument(
        "--contributor-id",
        dest="contributor_ids",
        action="append",
        default=[],
        help="Exact contributor_id to include (can be passed multiple times; OR logic)",
    )
    p_fmt.add_argument(
        "--output",
        type=Path,
        default=Path("output/fec_formatted.xlsx"),
        help="Output XLSX path (default: output/fec_formatted.xlsx)",
    )
    # combine
    p_comb = sub.add_parser("combine", help="Combine CSV files from a directory")
    p_comb.add_argument("--input-dir", type=Path, required=True, help="Directory containing CSV files")
    p_comb.add_argument("--pattern", type=str, default="*.csv", help="Glob pattern (default: *.csv)")
    p_comb.add_argument("--output", type=Path, required=True, help="Output combined CSV path")
    p_comb.add_argument("--overwrite", action="store_true", help="Allow overwriting output")

    ns = parser.parse_args(argv)
    # For uniformity, we still return Args for format-xlsx; combine handled in main()
    contrib_names = tuple(getattr(ns, "contributor_names", []) or [])
    contrib_name_contains = tuple(getattr(ns, "contributor_name_contains", []) or [])
    contrib_ids = tuple(getattr(ns, "contributor_ids", []) or [])
    input_file = getattr(ns, "input_file", None) or Path("")
    output = getattr(ns, "output", None) or Path("output/out.csv")
    # Pack contains list back into Args via a dynamic attribute on the namespace we return alongside Args
    args = Args(input_file=input_file, contributor_names=contrib_names, contributor_ids=contrib_ids, output_path=output)
    # Attach for use in run_format
    setattr(args, "contributor_name_contains", contrib_name_contains)
    return args


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def matches_filters(row: List[str], header: List[str], names: Sequence[str], ids: Sequence[str]) -> bool:
    if not names and not ids:
        return True
    name_idx = header.index("contributor_name") if "contributor_name" in header else -1
    id_idx = header.index("contributor_id") if "contributor_id" in header else -1

    name_match = False
    id_match = False

    if names and name_idx >= 0:
        value = row[name_idx]
        name_match = value in names

    if ids and id_idx >= 0:
        value = row[id_idx]
        id_match = value in ids

    return name_match or id_match


def build_recipient(header: List[str], row: List[str]) -> str:
    committee_name = row[header.index("committee_name")] if "committee_name" in header else ""
    committee_id = row[header.index("committee_id")] if "committee_id" in header else ""
    return f"{committee_name} ({committee_id})".strip()


def build_contributor(header: List[str], row: List[str]) -> str:
    name = row[header.index("contributor_name")] if "contributor_name" in header else ""
    contrib_id = row[header.index("contributor_id")] if "contributor_id" in header else ""
    if contrib_id and contrib_id != "C00401224":
        return f"{name} ({contrib_id})"
    return name


def build_address(header: List[str], row: List[str]) -> str:
    parts = [
        row[header.index("contributor_street_1")] if "contributor_street_1" in header else "",
        row[header.index("contributor_street_2")] if "contributor_street_2" in header else "",
    ]
    street = ", ".join([p for p in parts if p]).strip(", ")
    city = row[header.index("contributor_city")] if "contributor_city" in header else ""
    state = row[header.index("contributor_state")] if "contributor_state" in header else ""
    zip_code = row[header.index("contributor_zip")] if "contributor_zip" in header else ""
    prefix = street if street else ""
    suffix = ", ".join([c for c in [city, state] if c])
    if prefix and suffix:
        base = f"{prefix}, {suffix}"
    else:
        base = prefix or suffix
    return f"{base} {zip_code}".strip()


def build_employer_occupation(header: List[str], row: List[str]) -> str:
    employer = row[header.index("contributor_employer")] if "contributor_employer" in header else ""
    occupation = row[header.index("contributor_occupation")] if "contributor_occupation" in header else ""
    if employer or occupation:
        if employer and occupation:
            return f"{occupation}/{employer}"
        return employer or occupation
    return ""


def get_value(header: List[str], row: List[str], column: str) -> str:
    return row[header.index(column)] if column in header else ""


def build_row(header: List[str], row: List[str]) -> List[str]:
    recipient = build_recipient(header, row)
    contributor = build_contributor(header, row)
    address = build_address(header, row)
    occ_emp = build_employer_occupation(header, row)
    date = get_value(header, row, "contribution_receipt_date")
    amount = get_value(header, row, "contribution_receipt_amount")
    fec_id = get_value(header, row, "image_number")
    return [recipient, contributor, address, occ_emp, date, amount, fec_id]


def write_xlsx(rows_with_links: Iterable[Tuple[List[str], Optional[str]]], output_path: Path, writer: XLSXWriterService) -> None:
    ensure_parent_dir(output_path)
    writer.write(rows_with_links, output_path)


def run_format(args: Args) -> Path:
    container = Container()
    builder = container.create_row_builder()
    writer = container.create_xlsx_writer()
    with args.input_file.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            raise SystemExit("[ERROR] Input file is empty")

        typed_rows: List[Tuple[List[str], Optional[str], Optional[datetime]]] = []
        pdf_idx = header.index("pdf_url") if "pdf_url" in header else -1
        for row in reader:
            if not row:
                continue
            if not builder.matches_filters(row, header, args.contributor_names, args.contributor_ids, getattr(args, "contributor_name_contains", ())):
                continue
            pdf_url = row[pdf_idx] if pdf_idx >= 0 and pdf_idx < len(row) else None
            values = build_row(header, row)
            date_str = values[OUTPUT_COLUMNS.index("Contribution Date")]
            dt = _parse_date(date_str)
            typed_rows.append((values, pdf_url, dt))

    # Sort reverse-chronologically by date, keeping None dates last
    def _cmp(a: Tuple[List[str], Optional[str], Optional[datetime]],
             b: Tuple[List[str], Optional[str], Optional[datetime]]) -> int:
        da = a[2]
        db = b[2]
        if da is None and db is None:
            return 0
        if da is None:
            return 1
        if db is None:
            return -1
        if da > db:
            return -1
        if da < db:
            return 1
        return 0

    typed_rows.sort(key=cmp_to_key(_cmp))
    output_rows: List[Tuple[List[str], Optional[str]]] = [(v, link) for (v, link, _dt) in typed_rows]

    write_xlsx(output_rows, args.output_path, writer)
    print(f"[SUCCESS] Wrote {len(output_rows)} rows to '{args.output_path}'")
    return args.output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="FEC Data Tools")
    # Parse once using our helper to keep type structure
    ns = argparse.Namespace()
    # Reuse parse_args for structured Args and to bind subcommands
    args = parse_args()

    # Re-parse to know which subcommand was used
    import sys
    full_ns = argparse.ArgumentParser(add_help=False)
    # Minimal reparse to find command
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = ""

    if command == "combine":
        # Manually parse combine args again
        comb_parser = argparse.ArgumentParser(prog="combine")
        comb_parser.add_argument("--input-dir", type=Path, required=True)
        comb_parser.add_argument("--pattern", type=str, default="*.csv")
        comb_parser.add_argument("--output", type=Path, required=True)
        comb_parser.add_argument("--overwrite", action="store_true")
        comb_ns, _ = comb_parser.parse_known_args(sys.argv[2:])
        combiner = CSVCombinerService()
        result = combiner.combine(
            input_dir=comb_ns.input_dir,
            output_path=comb_ns.output,
            pattern=comb_ns.pattern,
            overwrite=bool(comb_ns.overwrite),
        )
        print(f"[SUCCESS] Combined {result.files_combined} files, wrote {result.rows_written} rows to '{result.output_path}'")
        return
    else:
        run_format(args)


if __name__ == "__main__":
    main()


