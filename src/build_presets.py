#!/usr/bin/env python3
# Copyright 2026 weekssa and contributors
# SPDX-License-Identifier: Apache-2.0
#
# ToneBoosters/UAPP normalization and XML mapping in this file is based in
# part on SiliconExarch/EqConverter (Apache-2.0). This implementation has
# been substantially rewritten and extended for OPRA. See NOTICE.
"""Build ToneBoosters/UAPP 10-band XML presets from the OPRA JSONL feed."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
import re
import shutil
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET

DEFAULT_OPRA_URL = "https://opra.roonlabs.net/database_v1.jsonl"
F_MIN = 16.0
F_MAX = 20000.0
GAIN_MIN = -20.0
GAIN_MAX = 20.0
Q_MIN = 0.1
Q_MAX = 10.0
MAX_BANDS = 10

TB_FILTER_TYPES = {
    "low_shelf": 0.071428575,
    "peak_dip": 0.21428572,
    "high_shelf": 0.2857143,
}

DISABLED_FILTER = {
    "frequency": 0.9282573,
    "gain": 0.5,
    "enabled": 0,
    "q": 0.39434525,
    "type": TB_FILTER_TYPES["peak_dip"],
}

@dataclass(frozen=True)
class Target:
    vendor_id: str
    product_name: str
    output_path: str
    include_terms: tuple[str, ...] = ()


def load_config(path: Path) -> list[Target]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    targets = []
    for item in raw["targets"]:
        targets.append(Target(
            vendor_id=item["vendor_id"],
            product_name=item["product_name"],
            output_path=item["output_path"],
            include_terms=tuple(t.casefold() for t in item.get("include_terms", [])),
        ))
    return targets


def read_jsonl(source: str) -> Iterable[dict[str, Any]]:
    if re.match(r"^https?://", source):
        request = urllib.request.Request(source, headers={"User-Agent": "opra-uapp-converter/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if line:
                    yield json.loads(line)
    else:
        with Path(source).open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    yield json.loads(line)


def index_database(entries: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    vendors: dict[str, Any] = {}
    products: dict[str, Any] = {}
    eqs: list[dict[str, Any]] = []
    for entry in entries:
        kind = entry.get("type")
        entry_id = entry.get("id")
        data = entry.get("data", {})
        if kind == "vendor" and entry_id:
            vendors[entry_id] = data
        elif kind == "product" and entry_id:
            products[entry_id] = data
        elif kind == "eq" and entry_id:
            eqs.append({"id": entry_id, "data": data})
    return vendors, products, eqs


def uapp_safe_name(value: str) -> str:
    """Return a ToneBoosters/UAPP-safe name for ISO-8859-1 XML."""
    value = value.replace("•", "-")
    value = value.encode("iso-8859-1", errors="replace").decode("iso-8859-1")
    value = re.sub(r"[\\/:*?\"<>|]", "-", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value or "Preset"


def fmt(value: float) -> str:
    return format(float(f"{value:.8f}"), ".8g")


def normalize_frequency(freq: float) -> float:
    if not F_MIN <= freq <= F_MAX:
        raise ValueError(f"frequency {freq:g} Hz is outside UAPP/ToneBoosters range {F_MIN:g}-{F_MAX:g} Hz")
    return math.pow((freq - F_MIN) / (F_MAX - F_MIN), 1.0 / 3.0)


def normalize_gain(gain: float) -> float:
    if not GAIN_MIN <= gain <= GAIN_MAX:
        raise ValueError(f"gain {gain:g} dB is outside UAPP/ToneBoosters range {GAIN_MIN:g} to +{GAIN_MAX:g} dB")
    return (gain - GAIN_MIN) / (GAIN_MAX - GAIN_MIN)


def normalize_q(q: float) -> float:
    if not Q_MIN <= q <= Q_MAX:
        raise ValueError(f"Q {q:g} is outside UAPP/ToneBoosters range {Q_MIN:g}-{Q_MAX:g}")
    return math.pow((q - Q_MIN) / (Q_MAX - Q_MIN), 1.0 / 3.0)


def normalized_filter(band: dict[str, Any]) -> dict[str, Any]:
    band_type = band["type"]
    if band_type not in TB_FILTER_TYPES:
        raise ValueError(f"unsupported OPRA filter type for UAPP/ToneBoosters: {band_type}")
    if "q" not in band:
        raise ValueError(f"filter type {band_type} is missing Q")
    return {
        "frequency": normalize_frequency(float(band["frequency"])),
        "gain": normalize_gain(float(band.get("gain_db", 0.0))),
        "enabled": 1,
        "q": normalize_q(float(band["q"])),
        "type": TB_FILTER_TYPES[band_type],
    }


def build_xml(preset_name: str, gain_db: float, bands: list[dict[str, Any]]) -> tuple[str, list[str]]:
    warnings: list[str] = []
    if len(bands) > MAX_BANDS:
        warnings.append(f"OPRA has {len(bands)} bands; UAPP supports 10, so only the first 10 priority-sorted bands were used.")
        bands = bands[:MAX_BANDS]

    filters = [normalized_filter(band) for band in bands]
    while len(filters) < MAX_BANDS:
        filters.append(dict(DISABLED_FILTER))

    root = ET.Element("Preset")
    info = ET.SubElement(root, "PresetInfo", {"Name": preset_name, "TenBand": "1"})
    for flt in filters:
        for value in (flt["frequency"], flt["gain"], flt["enabled"], flt["q"], flt["type"], 0):
            ET.SubElement(info, "Value").text = fmt(value) if isinstance(value, float) else str(value)

    preamp = normalize_gain(float(gain_db))
    for value in (0, preamp, 1, 0.33333334, 0.05, 0):
        ET.SubElement(info, "Value").text = fmt(value) if isinstance(value, float) else str(value)

    body = ET.tostring(root, encoding="unicode", short_empty_elements=False)
    xml = '<?xml version="1.0" encoding="ISO-8859-1"?>\n' + body + "\n"
    return xml, warnings


def target_matches(target: Target, product: dict[str, Any], eq_id: str, eq: dict[str, Any]) -> bool:
    if product.get("vendor_id") != target.vendor_id:
        return False
    if product.get("name", "").casefold() != target.product_name.casefold():
        return False
    if not target.include_terms:
        return True
    haystack = " ".join((eq_id, str(eq.get("details", "")), str(eq.get("author", "")))).casefold()
    return any(term in haystack for term in target.include_terms)


def preset_display_name(eq: dict[str, Any]) -> str:
    author = str(eq.get("author", "Unknown"))
    details = str(eq.get("details", "")).strip()
    return uapp_safe_name(f"{author} - {details}" if details else author)


def write_presets(source: str, config_path: Path, output_root: Path) -> dict[str, Any]:
    targets = load_config(config_path)
    vendors, products, eqs = index_database(read_jsonl(source))

    candidates: list[tuple[Target, str, dict[str, Any], str, dict[str, Any]]] = []
    matched_counts = {target.output_path: 0 for target in targets}
    for eq_entry in eqs:
        eq_id = eq_entry["id"]
        eq = eq_entry["data"]
        if eq.get("type") != "parametric_eq":
            continue
        product_id = eq.get("product_id")
        product = products.get(product_id)
        if not product:
            continue
        for target in targets:
            if target_matches(target, product, eq_id, eq):
                matched_counts[target.output_path] += 1
                candidates.append((target, eq_id, eq, product_id, product))

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    name_counts = Counter((target.output_path, preset_display_name(eq)) for target, _, eq, _, _ in candidates)
    used_paths: set[str] = set()
    manifest_entries: list[dict[str, Any]] = []
    errors: list[str] = []

    for target, eq_id, eq, product_id, product in candidates:
        try:
            params = eq["parameters"]
            bands = list(params.get("bands", []))
            base_name = preset_display_name(eq)
            name = base_name
            if name_counts[(target.output_path, base_name)] > 1:
                name = uapp_safe_name(f"{base_name} - {len(bands)} band")
            destination = output_root / target.output_path / f"{name}.xml"
            if destination.as_posix().casefold() in used_paths:
                short_id = eq_id.split("::")[-1]
                name = uapp_safe_name(f"{name} - {short_id}")
                destination = output_root / target.output_path / f"{name}.xml"
            used_paths.add(destination.as_posix().casefold())
            destination.parent.mkdir(parents=True, exist_ok=True)

            xml, warnings = build_xml(name, float(params.get("gain_db", 0.0)), bands)
            destination.write_text(xml, encoding="iso-8859-1")
            vendor = vendors.get(target.vendor_id, {})
            manifest_entries.append({
                "file": destination.relative_to(output_root).as_posix(),
                "opra_eq_id": eq_id,
                "opra_product_id": product_id,
                "vendor": vendor.get("name", target.vendor_id),
                "product": product.get("name", target.product_name),
                "author": eq.get("author"),
                "details": eq.get("details"),
                "source_link": eq.get("link"),
                "preamp_db": params.get("gain_db", 0.0),
                "opra_band_count": len(bands),
                "uapp_band_count": min(len(bands), MAX_BANDS),
                "warnings": warnings,
            })
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{eq_id}: {exc}")

    missing = [path for path, count in matched_counts.items() if count == 0]
    if missing:
        errors.extend(f"No matching OPRA EQ entries found for configured output {path}" for path in missing)

    manifest = {
        "opra_source": source,
        "opra_attribution": "EQ data from the OPRA project (CC BY-SA 4.0). Preset creators are credited per file in this manifest.",
        "preset_count": len(manifest_entries),
        "presets": sorted(manifest_entries, key=lambda item: item["file"].casefold()),
        "errors": errors,
    }
    (output_root / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if errors:
        raise RuntimeError("Preset generation failed:\n- " + "\n- ".join(errors))
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=DEFAULT_OPRA_URL, help="OPRA database_v1.jsonl URL or local file")
    parser.add_argument("--config", type=Path, default=Path("config/targets.json"))
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()
    try:
        manifest = write_presets(args.source, args.config, args.output)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Generated {manifest['preset_count']} UAPP/ToneBoosters presets in {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
