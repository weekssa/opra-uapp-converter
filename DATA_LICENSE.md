# Data licensing and attribution

This repository contains software and OPRA-derived data with different licensing.

## Converter software and project documentation

The converter source code, tests, configuration format, and project documentation in this repository are distributed under the Apache License, Version 2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

The ToneBoosters/UAPP normalization and XML mapping is based in part on `SiliconExarch/EqConverter`, which is also licensed under Apache-2.0. The implementation here has been substantially rewritten and extended for OPRA ingestion, validation, multiple filter types, deterministic output, attribution metadata, generated documentation, and managed Drive workflows. The upstream attribution is preserved in `NOTICE` and in the source-file provenance notice.

## OPRA-derived data and generated presets

The headphone/product/EQ data consumed from the OPRA project is licensed by OPRA under the Creative Commons Attribution-ShareAlike 4.0 International license (CC BY-SA 4.0).

The generated files under `output/` and the OPRA-derived metadata in `output/manifest.json` are format conversions and/or reproductions of OPRA dataset material. To the extent copyright or database rights apply to that material, those OPRA-derived portions are distributed under CC BY-SA 4.0, not under the repository's Apache-2.0 software license.

Attribution is preserved in `output/manifest.json`:

- `author` identifies the EQ creator supplied by OPRA.
- `details` preserves the OPRA tuning/measurement description.
- `source_link` preserves the source link when OPRA provides one.
- `opra_eq_id` and `opra_product_id` preserve the OPRA identifiers.
- `opra_source` identifies the supported OPRA distribution feed used to build the presets.

OPRA source repository: https://github.com/opra-project/OPRA

OPRA distribution feed used by this converter: https://opra.roonlabs.net/database_v1.jsonl

CC BY-SA 4.0 license: https://creativecommons.org/licenses/by-sa/4.0/

## Compatibility names and trademarks

USB Audio Player PRO (UAPP), ToneBoosters, manufacturer names, and headphone/product names are used only to describe compatibility or identify source data. Their respective trademarks and product names remain the property of their owners. This project is not affiliated with or endorsed by OPRA, ToneBoosters, USB Audio Player PRO, or the headphone manufacturers.

## Third-party implementation provenance

The principal third-party implementation reference incorporated into the converter is:

- `SiliconExarch/EqConverter` — Apache License 2.0 — https://github.com/SiliconExarch/EqConverter

Other publicly available community tools may be useful for compatibility cross-checking, but this repository does not redistribute their source merely by naming or comparing against them.
