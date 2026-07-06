from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SlusiLccReport(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    enable: int
    state: str
    district: str
    report_no: str
    year: int | None = None
    total_area_ha: int | None = None
    lcc_class_i: int | None = None
    lcc_class_ii: int | None = None
    lcc_class_iii: int | None = None
    lcc_class_iv: int | None = None
    lcc_class_v: int | None = None
    lcc_class_vi: int | None = None
    lcc_class_vii: int | None = None
    lcc_class_viii: int | None = None
    forest_area: int | None = None
    miscellaneous_area: int | None = None
    spatial_available: bool | None = None
    non_spatial_available: bool | None = None
    ingested_at: datetime
