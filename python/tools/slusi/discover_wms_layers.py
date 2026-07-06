#!/usr/bin/env python3
"""CLI: probe SHC WMS layers for a given state/district and report availability."""
from __future__ import annotations

import argparse
import asyncio
import os

import httpx

from base import SLUSIToolBase
from app.services.shc_fetcher import SHCFetcher, SRM_LAYERS, _NUTRIENT_FIELD_MAP

NUTRIENT_STYLES = list(_NUTRIENT_FIELD_MAP.keys())


async def _probe_style(
    client: httpx.AsyncClient,
    wms_url: str,
    layer_name: str,
    style: str,
    bbox: str,
    width: str,
    height: str,
    i: str,
    j: str,
    feature_count: str,
) -> tuple[str, str | None]:
    params = {
        "SERVICE": "WMS", "VERSION": "1.3.0", "REQUEST": "GetFeatureInfo",
        "LAYERS": layer_name, "QUERY_LAYERS": layer_name, "STYLES": style,
        "CRS": "EPSG:4326", "BBOX": bbox,
        "WIDTH": width, "HEIGHT": height, "I": i, "J": j,
        "INFO_FORMAT": "application/json", "FEATURE_COUNT": feature_count,
    }
    try:
        resp = await client.get(wms_url, params=params, timeout=8)
        if resp.status_code != 200:
            return (style, None)
        body = resp.json()
        features = body.get("features", [])
        if not features:
            return (style, None)
        props = features[0].get("properties", {})
        val = next((str(v) for v in props.values() if v not in (None, "", 0, "0")), None)
        return (style, val)
    except Exception:
        return (style, None)


async def _run(args: argparse.Namespace) -> None:
    base = SLUSIToolBase(env_file=args.env_file)
    if args.wms_path:
        os.environ["SHC_WMS_PATH"] = args.wms_path

    from app.core.config import settings
    if not settings.SHC_WMS_PATH:
        print("ERROR: SHC_WMS_PATH not set")
        return

    fetcher = SHCFetcher()
    layers_data = await fetcher.get_district_layers(args.state_code, args.district_code)
    fixed_layers = layers_data.get("fixedLayers", [])
    shc_layers = layers_data.get("shcLayers", [])
    bbox_dict = layers_data.get("bbox", {})
    cycle = args.cycle or (shc_layers[-1] if shc_layers else settings.SHC_CYCLE)

    wms_url = f"{settings.SHC_WMS_BASE}/{settings.SHC_WMS_PATH}"
    sc, dc = args.state_code, args.district_code

    print(f"\nDistrict bbox: {bbox_dict}")
    print(f"Available SHC cycles: {shc_layers}")
    print(f"Probing cycle: {cycle}\n")

    district_bbox = f"{bbox_dict.get('minx')},{bbox_dict.get('miny')},{bbox_dict.get('maxx')},{bbox_dict.get('maxy')}"

    async with httpx.AsyncClient(timeout=15) as client:
        # Probe 7 SRM layers
        print("SRM layers (coordinate-based BBOX):")
        srm_tasks = []
        for layer in fixed_layers:
            code = layer.get("code", "")
            prop = next((p for c, p in SRM_LAYERS if c == code), code)
            srm_tasks.append(
                _probe_style(client, wms_url, layer["layerName"], layer["style"],
                             f"{args.lon - 0.005},{args.lat - 0.005},{args.lon + 0.005},{args.lat + 0.005}",
                             "101", "101", "50", "50", "1")
            )
        srm_results = await asyncio.gather(*srm_tasks)
        for (style, val), layer in zip(srm_results, fixed_layers):
            status = f"✓  {val}" if val else "✗  no data"
            print(f"  {layer.get('code', ''):<20} {status}")

        # Probe SHC nutrient layer
        print(f"\nSHC nutrient layer ({cycle}):")
        shc_layer = f"{sc}_{dc}_shc_{cycle}"
        nut_style, nut_val = await _probe_style(
            client, wms_url, shc_layer, "N",
            district_bbox, "256", "256", "128", "128", "100"
        )
        print(f"  {shc_layer:<40} {'✓  data found' if nut_val else '✗  no data'}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover available SHC WMS layers")
    parser.add_argument("--state-code", dest="state_code", type=int, required=True)
    parser.add_argument("--district-code", dest="district_code", type=int, required=True)
    parser.add_argument("--lat", type=float, default=0.0, help="Lat for SRM probe (centre of district)")
    parser.add_argument("--lon", type=float, default=0.0, help="Lon for SRM probe")
    parser.add_argument("--cycle", default=None)
    parser.add_argument("--wms-path", dest="wms_path", default=None)
    parser.add_argument("--env-file", dest="env_file", default=None)
    args = parser.parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
