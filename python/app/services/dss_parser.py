"""DSS HTML parser and PrettyPrinter for SLUSI LCC data."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from app.schemas.slusi import LCCReport, SHCSoilProfile

logger = logging.getLogger(__name__)

# Expected DSS table column headers (case-insensitive substring match)
_EXPECTED_COLS = [
    "state", "district", "report", "year", "area",
    "class i", "class ii", "class iii", "class iv",
    "class v", "class vi", "class vii", "class viii",
    "forest", "misc",
]

# Column index mapping after header detection
_COL_MAP = {
    "state": 0,
    "district": 1,
    "report_no": 2,
    "year": 3,
    "total_area_ha": 4,
    "lcc_class_i": 5,
    "lcc_class_ii": 6,
    "lcc_class_iii": 7,
    "lcc_class_iv": 8,
    "lcc_class_v": 9,
    "lcc_class_vi": 10,
    "lcc_class_vii": 11,
    "lcc_class_viii": 12,
    "forest_area": 13,
    "miscellaneous_area": 14,
    "spatial_available": 15,
    "non_spatial_available": 16,
}

# Delimiter used by PrettyPrinter / parse_single_row
_SEP = "\t"


class SchemaMismatchError(Exception):
    """Raised when the DSS HTML table structure doesn't match expectations."""


def _parse_cell(value: str) -> float | None:
    """Return float for numeric strings, None for dash/empty."""
    v = value.strip()
    if v in ("", "-", "N/A", "NA"):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def _parse_bool(value: str) -> bool:
    v = value.strip().lower()
    return v in ("yes", "true", "1", "y")


class DSSParser:
    """Parses the SLUSI DSS HTML table into LCCReport objects."""

    def parse(self, html: str) -> list[LCCReport]:
        """
        Parse DSS HTML table. Skips malformed rows with a warning.
        Raises SchemaMismatchError if expected columns are not found.
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        if table is None:
            raise SchemaMismatchError("No <table> found in DSS HTML")

        rows = table.find_all("tr")
        if not rows:
            raise SchemaMismatchError("DSS table has no rows")

        # Detect header row
        header_row = rows[0]
        headers = [th.get_text(strip=True).lower() for th in header_row.find_all(["th", "td"])]

        # Validate at least a few expected columns exist
        found = sum(1 for col in _EXPECTED_COLS if any(col in h for h in headers))
        if found < 5:
            raise SchemaMismatchError(
                f"DSS table schema mismatch: only {found}/{len(_EXPECTED_COLS)} "
                f"expected columns found. Headers: {headers}"
            )

        reports: list[LCCReport] = []
        for row_idx, row in enumerate(rows[1:], start=1):
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if len(cells) < 15:
                logger.warning("DSS row %d: too few cells (%d), skipping", row_idx, len(cells))
                continue
            try:
                report = LCCReport(
                    state=cells[_COL_MAP["state"]],
                    district=cells[_COL_MAP["district"]],
                    report_no=cells[_COL_MAP["report_no"]],
                    year=int(cells[_COL_MAP["year"]]) if cells[_COL_MAP["year"]].strip().isdigit() else None,
                    total_area_ha=_parse_cell(cells[_COL_MAP["total_area_ha"]]),
                    lcc_class_i=_parse_cell(cells[_COL_MAP["lcc_class_i"]]),
                    lcc_class_ii=_parse_cell(cells[_COL_MAP["lcc_class_ii"]]),
                    lcc_class_iii=_parse_cell(cells[_COL_MAP["lcc_class_iii"]]),
                    lcc_class_iv=_parse_cell(cells[_COL_MAP["lcc_class_iv"]]),
                    lcc_class_v=_parse_cell(cells[_COL_MAP["lcc_class_v"]]),
                    lcc_class_vi=_parse_cell(cells[_COL_MAP["lcc_class_vi"]]),
                    lcc_class_vii=_parse_cell(cells[_COL_MAP["lcc_class_vii"]]),
                    lcc_class_viii=_parse_cell(cells[_COL_MAP["lcc_class_viii"]]),
                    forest_area=_parse_cell(cells[_COL_MAP["forest_area"]]),
                    miscellaneous_area=_parse_cell(cells[_COL_MAP["miscellaneous_area"]]),
                    spatial_available=_parse_bool(cells[_COL_MAP["spatial_available"]]) if len(cells) > 15 else False,
                    non_spatial_available=_parse_bool(cells[_COL_MAP["non_spatial_available"]]) if len(cells) > 16 else False,
                    ingested_at=datetime.now(timezone.utc),
                )
                reports.append(report)
            except Exception as exc:
                logger.warning("DSS row %d: parse error (%s), skipping", row_idx, exc)

        return reports

    def parse_single_row(self, text: str) -> LCCReport:
        """
        Parse a single tab-separated row produced by PrettyPrinter.format_lcc_report.
        Used for round-trip property testing.
        """
        parts = text.split(_SEP)
        if len(parts) < 17:
            raise ValueError(f"Expected ≥17 tab-separated fields, got {len(parts)}")

        def _f(idx: int) -> float | None:
            return _parse_cell(parts[idx])

        def _b(idx: int) -> bool:
            return _parse_bool(parts[idx]) if idx < len(parts) else False

        return LCCReport(
            state=parts[0].strip(),
            district=parts[1].strip(),
            report_no=parts[2].strip(),
            year=int(parts[3]) if parts[3].strip().isdigit() else None,
            total_area_ha=_f(4),
            lcc_class_i=_f(5),
            lcc_class_ii=_f(6),
            lcc_class_iii=_f(7),
            lcc_class_iv=_f(8),
            lcc_class_v=_f(9),
            lcc_class_vi=_f(10),
            lcc_class_vii=_f(11),
            lcc_class_viii=_f(12),
            forest_area=_f(13),
            miscellaneous_area=_f(14),
            spatial_available=_b(15),
            non_spatial_available=_b(16),
            ingested_at=datetime.fromisoformat(parts[17].strip()) if len(parts) > 17 else datetime.now(timezone.utc),
        )


class PrettyPrinter:
    """Formats SLUSI data structures back to human-readable / round-trippable text."""

    def format_lcc_report(self, report: LCCReport) -> str:
        """
        Serialise an LCCReport to a tab-separated string.
        Parseable back to an equivalent LCCReport via DSSParser.parse_single_row.
        """
        def _v(val: float | None) -> str:
            return str(val) if val is not None else "-"

        def _b(val: bool) -> str:
            return "yes" if val else "no"

        fields = [
            report.state,
            report.district,
            report.report_no,
            str(report.year) if report.year is not None else "-",
            _v(report.total_area_ha),
            _v(report.lcc_class_i),
            _v(report.lcc_class_ii),
            _v(report.lcc_class_iii),
            _v(report.lcc_class_iv),
            _v(report.lcc_class_v),
            _v(report.lcc_class_vi),
            _v(report.lcc_class_vii),
            _v(report.lcc_class_viii),
            _v(report.forest_area),
            _v(report.miscellaneous_area),
            _b(report.spatial_available),
            _b(report.non_spatial_available),
            report.ingested_at.isoformat(),
        ]
        return _SEP.join(fields)

    def format_shc_soil_profile(self, profile: SHCSoilProfile) -> dict[str, object]:
        """
        Serialise a SHCSoilProfile to a dict that can be deserialised back
        via SHCSoilProfile.model_validate (round-trip property).
        """
        return json.loads(profile.model_dump_json())
