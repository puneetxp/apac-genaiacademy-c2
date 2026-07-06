#!/usr/bin/env python3
"""CLI: seed shc_state_district_codes table from the SHC GraphQL API."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

from base import SLUSIToolBase


async def _run(args: argparse.Namespace) -> None:
    base = SLUSIToolBase(env_file=args.env_file)
    mapper = base.get_mapper()

    if args.db_url:
        os.environ["DATABASE_URL"] = args.db_url

    if args.verify_existing:
        db = base.get_session()
        if db is None:
            print("ERROR: DATABASE_URL not set", file=sys.stderr)
            sys.exit(1)
        from sqlalchemy import text
        existing = {
            (row[0], row[1]): (row[2], row[3])
            for row in db.execute(
                text("SELECT state_name, district_name, state_code, district_code FROM shc_state_district_codes")
            ).fetchall()
        }
        states = await mapper.get_all_states()
        mismatches = 0
        for state in states:
            districts = await mapper.get_districts(state["_id"])
            for district in districts:
                key = (state["name"], district["name"])
                if key in existing:
                    sc, dc = existing[key]
                    if sc != int(state["code"]) or dc != int(district["code"]):
                        print(f"MISMATCH: {state['name']} / {district['name']}: DB=({sc},{dc}) API=({state['code']},{district['code']})")
                        mismatches += 1
        print(f"\n{mismatches} mismatches found" if mismatches else "All codes match ✓")
        return

    if args.db_url or os.getenv("DATABASE_URL"):
        db = base.get_session()
        if db is None:
            print("ERROR: DATABASE_URL not set", file=sys.stderr)
            sys.exit(1)
        count = await mapper.seed_database(db)
        print(f"Seeded {count} state/district rows into shc_state_district_codes")
        return

    # Default: print JSON to stdout or file
    states = await mapper.get_all_states()
    mapping: dict[str, dict[str, int]] = {}
    for state in states:
        districts = await mapper.get_districts(state["_id"])
        mapping[state["name"]] = {
            "_code": int(state["code"]),
            **{d["name"]: int(d["code"]) for d in districts},
        }

    output = json.dumps(mapping, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Written to {args.output}")
    else:
        print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed SHC state/district codes from GraphQL API")
    parser.add_argument("--output", default=None, help="Output JSON file path (default: stdout)")
    parser.add_argument("--db-url", dest="db_url", default=None, help="PostgreSQL URL to upsert into DB")
    parser.add_argument("--verify-existing", dest="verify_existing", action="store_true",
                        help="Re-fetch from GraphQL and report changed codes vs DB")
    parser.add_argument("--env-file", dest="env_file", default=None)
    args = parser.parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
