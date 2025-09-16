from __future__ import annotations

from fec_formatter.services import FECRowBuilder


def test_exact_and_contains_filters():
    builder = FECRowBuilder()
    header = ["contributor_name", "contributor_id"]
    row = ["National Association of Realtors Political Action Committee", "X"]
    # Exact match
    assert builder.matches_filters(row, header, ["National Association of Realtors Political Action Committee"], [], ())
    # Case-insensitive whitespace-normalized
    assert builder.matches_filters(row, header, ["  national  association of  realtors political  action  committee  "], [], ())
    # Contains match
    assert builder.matches_filters(row, header, [], [], ("realtors",))
    # No match
    assert not builder.matches_filters(row, header, ["Other"], [], ())

