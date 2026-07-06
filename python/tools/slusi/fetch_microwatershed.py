#!/usr/bin/env python3
"""CLI: download SLUSI microwatershed PNG maps."""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

import httpx
from bs4 import BeautifulSoup

from base import SLUSIToolBase
from app.services.slusi_service import SLUSIService

MWA_URL = "https://slusi.da.gov.in/mwanew.html"


async def _run(args: argparse.Namespace) -> None:
    base = SLUSIToolBase(env_file=args.env_file)

    if args.save_db:
        db = base.get_session()
        if db is None:
            print("ERROR: DATABASE_URL not set", file=sys.stderr)
            sys.exit(1)
        service = SLUSIService(db)
        count = await service.ingest_microwatershed_maps()
        print(f"Downloaded and stored {count} maps")
        return

    out_dir = args.out or "./output/maps"
    os.makedirs(out_dir, exist_ok=True)

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(MWA_URL)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        links: list[tuple[str, str]] = []
        for a in soup.find_all("a", href=True):
            href: str = a["href"]
            if href.lower().endswith(".png"):
                name = a.get_text(strip=True) or href
                if not href.startswith("http"):
                    href = "https://slusi.da.gov.in/" + href.lstrip("/")
                links.append((name, href))

        if args.state:
            links = [(n, u) for n, u in links if n.lower() == args.state.lower()]

        for state_name, png_url in links:
            try:
                png_resp = await client.get(png_url)
                if png_resp.status_code != 200:
                    print(f"  ✗ {state_name}: HTTP {png_resp.status_code}")
                    continue
                safe_name = state_name.lower().replace(" ", "_") + ".png"
                dest = os.path.join(out_dir, safe_name)
                with open(dest, "wb") as f:
                    f.write(png_resp.content)
                print(f"  ✓ {state_name}: saved to {dest} ({len(png_resp.content)} bytes)")
            except Exception as exc:
                print(f"  ✗ {state_name}: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download SLUSI microwatershed maps")
    parser.add_argument("--state", default=None, help="State name to download")
    parser.add_argument("--all", action="store_true", help="Download all states")
    parser.add_argument("--out", default=None, help="Output directory")
    parser.add_argument("--save-db", dest="save_db", action="store_true")
    parser.add_argument("--db-url", dest="db_url", default=None)
    parser.add_argument("--env-file", dest="env_file", default=None)
    args = parser.parse_args()

    if args.db_url:
        os.environ["DATABASE_URL"] = args.db_url

    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
