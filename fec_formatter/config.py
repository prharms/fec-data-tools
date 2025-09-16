from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StyleConfig:
    base_font_name: str = "Garamond"
    base_font_size: int = 9
    header_fill_color: str = "FFD9D9D9"  # medium gray
    border_color: str = "FF000000"       # black
    hyperlink_underline: str = "single"
    amount_number_format: str = "$#,##0.00"
    date_number_format: str = "M/D/YYYY"


@dataclass(frozen=True)
class AppConfig:
    style: StyleConfig = StyleConfig()


