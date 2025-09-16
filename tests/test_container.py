from __future__ import annotations

from fec_formatter.container import Container


def test_container_creates_services():
    c = Container()
    assert c.create_row_builder() is not None
    assert c.create_xlsx_writer() is not None


