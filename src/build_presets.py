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
    include_eq_ids: tuple[str, ...] = ()
    allow_partial: bool = False


def load_config(path: Path) -> list[Target]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    targets = []
    for item in raw["targets"]:
        targets.append(Target(
            vendor_id=item["vendor_id"],
            product_name=item["product_name"],
            output_path=item["output_path"],
            include_terms=tuple(t.casefold() for t in item.get("include_terms", [])),
            include_eq_ids=tuple(str(eq_id).casefold() for eq_id in item.get("include_eq_ids", [])),
            allow_partial=bool(item.get("allow_partial", False)),
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


def target_path_parts(target: Target) -> list[str]:
    return [part.strip() for part in target.output_path.split("/") if part.strip()]


def target_display_label(target: Target) -> str:
    """Return the concise model/variant prefix shown in UAPP."""
    parts = target_path_parts(target)
    if len(parts) >= 2:
        return " ".join(parts[1:])
    return target.product_name


def target_variant_label(target: Target) -> str:
    """Return variant components beneath Manufacturer/Model, if any."""
    parts = target_path_parts(target)
    return " ".join(parts[2:]) if len(parts) >= 3 else ""


def compact_preset_details(target: Target, eq: dict[str, Any]) -> str:
    """Compact redundant wording for display without changing manifest metadata."""
    details = str(eq.get("details") or "").strip()
    if not details:
        return ""
    details = re.sub(r"^Measured\s+by\s+", "", details, count=1, flags=re.IGNORECASE).strip()
    variant = target_variant_label(target)
    if variant:
        details = re.sub(
            rf"\s*\(\s*{re.escape(variant)}\s*\)\s*$",
            "",
            details,
            count=1,
            flags=re.IGNORECASE,
        ).strip()
    return details


def preset_display_name(target: Target, eq: dict[str, Any]) -> str:
    """Build the UAPP-visible name: Model [Variant] - Creator - Details."""
    label = target_display_label(target)
    author = str(eq.get("author") or "Unknown").strip() or "Unknown"
    details = compact_preset_details(target, eq)
    parts = [label, author]
    if details:
        parts.append(details)
    return uapp_safe_name(" - ".join(parts))


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


def logical_product_name(value: str) -> str:
    """Normalize formatting-only product-name differences for coverage checks."""
    return "".join(char for char in value.casefold() if char.isalnum())


def logical_product_key(vendor_id: str, product_name: str) -> tuple[str, str]:
    return vendor_id.casefold(), logical_product_name(product_name)


def eq_fingerprint(eq: dict[str, Any]) -> str:
    """Fingerprint EQ semantics while ignoring source-link/provenance differences."""
    payload = {
        "author": str(eq.get("author", "")).casefold(),
        "details": str(eq.get("details", "")).casefold(),
        "type": eq.get("type"),
        "parameters": eq.get("parameters", {}),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def target_matches(target: Target, product: dict[str, Any], eq_id: str, eq: dict[str, Any]) -> bool:
    if product.get("vendor_id") != target.vendor_id:
        return False
    if product.get("name", "").casefold() != target.product_name.casefold():
        return False
    if target.include_eq_ids and eq_id.casefold() not in target.include_eq_ids:
        return False
    if not target.include_terms:
        return True
    haystack = " ".join((eq_id, str(eq.get("details", "")), str(eq.get("author", "")))).casefold()
    return any(term in haystack for term in target.include_terms)


def build_coverage_report(
    targets: list[Target],
    products: dict[str, Any],
    eqs: list[dict[str, Any]],
    candidates: list[tuple[Target, str, dict[str, Any], str, dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Ensure configured logical products do not silently omit OPRA parametric EQs."""
    groups: dict[tuple[str, str], list[Target]] = {}
    for target in targets:
        groups.setdefault(logical_product_key(target.vendor_id, target.product_name), []).append(target)

    matched_by_group: dict[tuple[str, str], dict[str, dict[str, Any]]] = {key: {} for key in groups}
    for target, eq_id, eq, _, product in candidates:
        key = logical_product_key(target.vendor_id, product.get("name", target.product_name))
        if key in matched_by_group:
            matched_by_group[key][eq_id] = eq

    report: list[dict[str, Any]] = []
    errors: list[str] = []
    for key, group_targets in sorted(groups.items()):
        vendor_id, normalized_name = key
        partial = any(target.allow_partial for target in group_targets)
        product_ids = {
            product_id
            for product_id, product in products.items()
            if product.get("vendor_id", "").casefold() == vendor_id
            and logical_product_name(str(product.get("name", ""))) == normalized_name
        }
        group_eqs = [
            entry for entry in eqs
            if entry["data"].get("type") == "parametric_eq"
            and entry["data"].get("product_id") in product_ids
        ]
        matched = matched_by_group.get(key, {})
        matched_fingerprints = {eq_fingerprint(eq) for eq in matched.values()}
        duplicate_covered: list[str] = []
        unmatched: list[str] = []
        for entry in group_eqs:
            eq_id = entry["id"]
            if eq_id in matched:
                continue
            if eq_fingerprint(entry["data"]) in matched_fingerprints:
                duplicate_covered.append(eq_id)
            else:
                unmatched.append(eq_id)

        display_names = sorted({str(products[product_id].get("name", "")) for product_id in product_ids})
        report.append({
            "vendor_id": group_targets[0].vendor_id,
            "logical_product": " / ".join(display_names) or group_targets[0].product_name,
            "mode": "partial" if partial else "complete",
            "opra_parametric_profiles": len(group_eqs),
            "matched_profiles": len(matched),
            "duplicate_profiles_covered": len(duplicate_covered),
            "unmatched_profiles": unmatched,
        })
        if unmatched and not partial:
            errors.append(
                f"Unmatched OPRA parametric EQ profiles for {group_targets[0].vendor_id} / "
                f"{' / '.join(display_names) or group_targets[0].product_name}: {', '.join(unmatched)}. "
                "Classify them with config targets, or set allow_partial=true only when the user explicitly wants a subset."
            )
    return report, errors


def write_presets(source: str, config_path: Path, output_root: Path) -> dict[str, Any]:
    targets = load_config(config_path)
    vendors, products, eqs = index_database(read_jsonl(source))

    candidates: list[tuple[Target, str, dict[str, Any], str, dict[str, Any]]] = []
    matched_counts = [0 for _ in targets]
    routing_errors: list[str] = []
    for eq_entry in eqs:
        eq_id = eq_entry["id"]
        eq = eq_entry["data"]
        if eq.get("type") != "parametric_eq":
            continue
        product_id = eq.get("product_id")
        product = products.get(product_id)
        if not product:
            continue
        matching_indices: list[int] = []
        for target_index, target in enumerate(targets):
            if target_matches(target, product, eq_id, eq):
                matching_indices.append(target_index)
                matched_counts[target_index] += 1
                candidates.append((target, eq_id, eq, product_id, product))
        output_paths = {targets[index].output_path for index in matching_indices}
        if len(output_paths) > 1:
            routing_errors.append(
                f"OPRA EQ {eq_id} matches multiple output folders: {', '.join(sorted(output_paths))}. "
                "Make the variant rules mutually exclusive instead of duplicating one profile across folders."
            )

    coverage, coverage_errors = build_coverage_report(targets, products, eqs, candidates)

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    name_counts = Counter((target.output_path, preset_display_name(target, eq)) for target, _, eq, _, _ in candidates)
    used_paths: set[str] = set()
    manifest_entries: list[dict[str, Any]] = []
    errors: list[str] = list(routing_errors) + list(coverage_errors)

    for target, eq_id, eq, product_id, product in candidates:
        try:
            params = eq["parameters"]
            bands = list(params.get("bands", []))
            base_name = preset_display_name(target, eq)
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
                "preset_name": name,
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

    missing = [target for target, count in zip(targets, matched_counts) if count == 0]
    if missing:
        errors.extend(
            f"No matching OPRA EQ entries found for configured target "
            f"{target.vendor_id} / {target.product_name} -> {target.output_path}"
            for target in missing
        )

    manifest = {
        "opra_source": source,
        "opra_attribution": "EQ data from the OPRA project (CC BY-SA 4.0). Preset creators are credited per file in this manifest.",
        "preset_count": len(manifest_entries),
        "presets": sorted(manifest_entries, key=lambda item: item["file"].casefold()),
        "coverage": coverage,
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
