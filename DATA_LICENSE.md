# Data licensing and attribution

This repository contains two different kinds of material with different licensing.

## Converter software and project documentation

The original converter source code, tests, configuration format, and project documentation in this repository are licensed under the MIT License. See [`LICENSE`](LICENSE).

## OPRA-derived data and generated presets

The headphone/product/EQ data consumed from the OPRA project is licensed by OPRA under the Creative Commons Attribution-ShareAlike 4.0 International license (CC BY-SA 4.0).

The generated files under `output/` and the OPRA-derived metadata in `output/manifest.json` are format conversions and/or reproductions of OPRA dataset material. To the extent copyright or database rights apply to that material, those OPRA-derived portions are distributed under CC BY-SA 4.0, not under the repository's MIT software license.

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

## Format references

The ToneBoosters/UAPP preset mapping was independently implemented using publicly available compatibility information and existing community converters as references. No third-party source code is included merely by referencing those projects. See the README for the named format references.
