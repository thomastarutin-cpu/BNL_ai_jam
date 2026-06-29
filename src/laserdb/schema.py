"""Lightweight schema checks."""

from pydantic import BaseModel, Field

from laserdb.constants import REQUIRED_COLUMNS


class DatabaseSchema(BaseModel):
    required_columns: list[str] = Field(default_factory=lambda: REQUIRED_COLUMNS.copy())

    def missing_columns(self, columns: list[str]) -> list[str]:
        return [column for column in self.required_columns if column not in columns]
