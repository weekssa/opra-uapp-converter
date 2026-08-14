# OPRA → UAPP ToneBoosters Preset Converter

Automatically converts selected [OPRA](https://github.com/opra-project/OPRA) parametric EQ profiles into 10-band ToneBoosters XML presets that can be imported into USB Audio Player PRO (UAPP).

## Included headphones

- HIFIMAN Edition XS
- SIMGOT EW300 Gold
- SIMGOT EW300 Silver
- SIMGOT EW300 DSP

Targets are configured in `config/targets.json`, so more headphones can be added without changing the converter.

## How it works

1. Downloads OPRA's supported `database_v1.jsonl` feed.
2. Matches configured headphones using OPRA vendor/product metadata.
3. Converts OPRA preamp, frequency, gain, Q, and supported filter types into ToneBoosters' normalized preset representation.
4. Writes UAPP-compatible `.xml` files under `output/`.
5. Writes `output/manifest.json` with OPRA IDs, creator attribution, source links, source band counts, and any conversion warnings.
6. GitHub Actions runs the converter daily and commits output changes automatically.

## Output folders

```text
output/
├── HIFIMAN/
│   └── Edition XS/
└── SIMGOT/
    └── EW300/
        ├── Gold/
        ├── Silver/
        └── DSP/
```

## UAPP / ToneBoosters behavior

UAPP's ToneBoosters preset format is a 10-band format. OPRA explicitly prioritizes its band list for software with limited band counts, so if an OPRA preset ever contains more than 10 bands this converter uses the first 10 and records a warning in the manifest.

The current converter intentionally supports the three filter types already established by community UAPP converters and used by the initial target presets:

- Peak / dip
- Low shelf
- High shelf

If OPRA later supplies an unsupported filter type for one of the configured targets, generation fails instead of silently producing an incorrect preset.

## Automatic updates

`.github/workflows/update-presets.yml` runs every day at 09:17 UTC and can also be started manually from the Actions tab. It also runs when converter/config/test files change.

## Run locally (optional)

No third-party Python packages are required.

```bash
python -m unittest discover -s tests -v
python src/build_presets.py
```

## Attribution and licenses

The converter code in this repository is independent project code.

OPRA manufacturer, product, and EQ data is licensed by the OPRA project under CC BY-SA 4.0. Generated preset metadata is tracked in `output/manifest.json`, including the individual EQ creator and source link where OPRA provides one. See the OPRA repository for complete attribution and licensing details.

## ToneBoosters format references

The ToneBoosters/UAPP XML mapping is based on the established open-source implementations `KassMiw/PEQ2UAPP` and `SiliconExarch/EqConverter`, with independent validation and stricter error handling here.
