from __future__ import annotations

from dataclasses import dataclass
from .config import AppConfig
from .services import FECRowBuilder, XLSXWriterService


@dataclass
class Container:
    config: AppConfig

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig()

    def create_row_builder(self) -> FECRowBuilder:
        return FECRowBuilder()

    def create_xlsx_writer(self) -> XLSXWriterService:
        return XLSXWriterService(self.config.style)




