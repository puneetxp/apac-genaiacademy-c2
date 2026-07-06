#!/usr/bin/env python3
"""CLI: scrape SLUSI DSS portal and display/store LCC data."""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys

import httpx

from base import SLUSIToolBase
from app.services.dss_parser import DSSParser
from app.services.slusi_service import SLUSIService

DSS_URL = "https://slusi.da.gov.in/dss/dss_report_wise.html"


async def _run(args: argparse.Namespace) -> None:
    base = SLUSIToolBase(env_file=args.env_file)
    parser = DSSParser()

    if args.save_db:
        db = base.get_session()
        if db is None:
            print("ERROR: DATABASE_URL not set", file=sys.stderr)
            sys.exit(1)
        service = SLUSIService(db)
        count = await service.ingest_lcc_data()
        print(f"Upserted {count} records into slusi_lcc_reports")
        return

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(DSS_URL)
        resp.raise_for_status()

    reports = parser.parse(resp.text)

    # Filter
    if args.state:
        reports = [r for r in reports if r.state.lower() == args.state.lower()]
    if args.district:
        reports = [r for r in reports if r.district.lower() == args.district.lower()]

    if not reports:
        print("No records found for the given filters.")
        return

    if args.output == "json":
        print(json.dumps([r.model_dump(mode="json") for r in reports], indent=2, default=str))
    elif args.output == "csv":
        writer = csv.DictWriter(sys.stdout, fieldnames=list(reports[0].model_fields.keys()))
        writer.writeheader()
        for r in reports:
            writer.writerow(r.model_dump(mode="json"))
    else:
        headers = ["Report No", "Year", "State", "District", "Area(ha)", "I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
        row_fmt = "{:<12} {:<6} {:<20} {:<20} {:<12} " + " ".join(["{:<8}"] * 8)
        print(row_fmt.format(*headers))
        print("-" * 120)
        for r in reports:
            print(row_fmt.format(
                r.report_no or "", r.year or "", r.state, r.district,
                r.total_area_ha or "-",
                r.lcc_class_i or "-", r.lcc_class_ii or "-", r.lcc_class_iii or "-",
                r.lcc_class_iv or "-", r.lcc_class_v or "-", r.lcc_class_vi or "-",
                r.lcc_class_vii or "-", r.lcc_class_viii or "-",
            ))


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch SLUSI DSS LCC data")
    parser.add_argument("--state", default=None)
    parser.add_argument("--district", default=None)
    parser.add_argument("--all", action="store_true", help="Fetch entire DSS table")
    parser.add_argument("--output", choices=["table", "json", "csv"], default="table")
    parser.add_argument("--save-db", dest="save_db", action="store_true")
    parser.add_argument("--db-url", dest="db_url", default=None)
    parser.add_argument("--env-file", dest="env_file", default=None)
    args = parser.parse_args()

    import os
    if args.db_url:
        os.environ["DATABASE_URL"] = args.db_url

    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
