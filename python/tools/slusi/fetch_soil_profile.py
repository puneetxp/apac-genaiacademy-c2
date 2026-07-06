#!/usr/bin/env python3
"""CLI: fetch all SHC WMS soil layers for a given GPS coordinate."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

from base import SLUSIToolBase
from app.services.dss_parser import PrettyPrinter


async def _run(args: argparse.Namespace) -> None:
    base = SLUSIToolBase(env_file=args.env_file)

    if args.wms_path:
        os.environ["SHC_WMS_PATH"] = args.wms_path

    # Resolve state/district codes
    mapper = base.get_mapper()
    db = base.get_session()
    if db is None:
        print("ERROR: DATABASE_URL not set — cannot resolve state/district codes", file=sys.stderr)
        sys.exit(1)

    codes = await mapper.resolve(args.state, args.district, db)
    if codes is None:
        print(f"ERROR: Could not resolve codes for state={args.state!r} district={args.district!r}", file=sys.stderr)
        sys.exit(1)

    state_code, district_code = codes
    fetcher = base.get_fetcher()
    profile = await fetcher.fetch_soil_profile(args.lat, args.lon, state_code, district_code)

    printer = PrettyPrinter()
    data = printer.format_shc_soil_profile(profile)

    if args.output == "json":
        print(json.dumps(data, indent=2, default=str))
    elif args.output == "csv":
        print(",".join(str(k) for k in data.keys()))
        print(",".join(str(v) for v in data.values()))
    else:
        # table
        print(f"{'Style':<30} {'Value'}")
        print("-" * 55)
        for k, v in data.items():
            print(f"{k:<30} {v}")
        print()
        print(f"Partial data: {'Yes' if profile.partial_data else 'No'}")
        if profile.fetched_at:
            print(f"Fetched at:   {profile.fetched_at.isoformat()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch SHC WMS soil profile for a coordinate")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--state", required=True, help="State name")
    parser.add_argument("--district", required=True, help="District name")
    parser.add_argument("--cycle", default=None, help="SHC cycle e.g. 2025-26")
    parser.add_argument("--output", choices=["table", "json", "csv"], default="table")
    parser.add_argument("--wms-path", dest="wms_path", default=None, help="Override SHC_WMS_PATH")
    parser.add_argument("--env-file", dest="env_file", default=None)
    args = parser.parse_args()

    if args.cycle:
        os.environ["SHC_CYCLE"] = args.cycle

    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
