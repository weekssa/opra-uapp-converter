# OPRA → UAPP ToneBoosters Preset Converter

Automatically converts selected [OPRA](https://github.com/opra-project/OPRA) parametric EQ profiles into 10-band ToneBoosters XML presets that can be imported into USB Audio Player PRO (UAPP), then mirrors the managed preset library to Google Drive.

## Project description

<!-- PROJECT_DESCRIPTION_START -->
OPRA → UAPP/ToneBoosters EQ converter with automatic Google Drive sync. Configured: HIFIMAN Edition XS; SIMGOT EW300 Gold; SIMGOT EW300 Silver; SIMGOT EW300 DSP
<!-- PROJECT_DESCRIPTION_END -->

The description above is generated from `config/targets.json`. The same generated text is also saved in [`docs/PROJECT_DESCRIPTION.md`](docs/PROJECT_DESCRIPTION.md) for easy copy/paste into repository or project metadata.

## Included headphones

<!-- SUPPORTED_HEADPHONES_START -->
- HIFIMAN Edition XS
- SIMGOT EW300 Gold
- SIMGOT EW300 Silver
- SIMGOT EW300 DSP
<!-- SUPPORTED_HEADPHONES_END -->

This list is generated automatically from `config/targets.json`, so adding or removing a target updates the documentation on the next GitHub build.

# The easy way to add a headphone

Use the ChatGPT Project connected to this repository and say:

> Add the FiiO FT1 to my OPRA UAPP presets.

The intended workflow is:

1. ChatGPT checks current OPRA data for the exact headphone and available EQ profiles.
2. ChatGPT updates `config/targets.json`.
3. GitHub Actions automatically rebuilds and validates the XML library.
4. GitHub Actions refreshes the README supported-headphones list and generated project description from the config.
5. ChatGPT verifies the generated manifest and, when Drive write access is available, immediately syncs the new/changed XML files into the matching folder under `Google Drive / OPRA UAPP Presets`.
6. The recurring Drive sync remains a safety net for later OPRA changes.
7. You access the XML from Drive and import it into UAPP.

The reusable Project Instructions are stored here:

[`docs/CHATGPT_PROJECT_INSTRUCTIONS.md`](docs/CHATGPT_PROJECT_INSTRUCTIONS.md)

For manual additions, including copy/paste JSON examples:

[`docs/ADDING_HEADPHONES.md`](docs/ADDING_HEADPHONES.md)

## How it works

1. Downloads OPRA's supported `database_v1.jsonl` feed.
2. Matches configured headphones using OPRA vendor/product metadata.
3. Converts OPRA preamp, frequency, gain, Q, and supported filter types into ToneBoosters' normalized preset representation.
4. Writes UAPP-compatible `.xml` files under `output/`.
5. Writes `output/manifest.json` with OPRA IDs, creator attribution, source links, source band counts, and any conversion warnings.
6. Regenerates the README supported-headphones section and project-description text from `config/targets.json`.
7. GitHub Actions runs the converter daily and whenever converter/config/test files change.
8. A scheduled ChatGPT task compares GitHub output with Google Drive and mirrors changed presets into `OPRA UAPP Presets`.

## Output folders

Current output:

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

New folders come directly from each target's `output_path` in `config/targets.json`.

For example:

```json
{
  "vendor_id": "fiio",
  "product_name": "FT1",
  "output_path": "FiiO/FT1"
}
```

would produce:

```text
output/FiiO/FT1/
```

and the Drive sync would manage:

```text
Google Drive/OPRA UAPP Presets/FiiO/FT1/
```

Only use a real OPRA `vendor_id` and exact OPRA product name. See the adding-headphones guide for how to find them.

## UAPP / ToneBoosters behavior

UAPP's ToneBoosters preset format is a 10-band format. OPRA explicitly prioritizes its band list for software with limited band counts, so if an OPRA preset ever contains more than 10 bands this converter uses the first 10 and records a warning in the manifest.

The current converter intentionally supports the three filter types already established by community UAPP converters and used by the initial target presets:

- Peak / dip
- Low shelf
- High shelf

If OPRA later supplies an unsupported filter type for one of the configured targets, generation fails instead of silently producing an incorrect preset.

## Automatic updates

`.github/workflows/update-presets.yml` runs every day at 09:17 UTC and can also be started manually from the Actions tab. It also runs automatically when converter/config/test files change.

On every run, `src/update_docs.py` regenerates the supported-headphones list in this README and `docs/PROJECT_DESCRIPTION.md` from `config/targets.json`. This keeps the documentation aligned even when you add a headphone manually.

The recurring Drive sync runs after the GitHub refresh. It reads `config/targets.json` and `output/manifest.json`, so adding a new configured `output_path` does **not** require manually editing the Drive automation.

When a headphone is added through the ChatGPT Project, the Project instructions tell ChatGPT to sync the affected Drive files immediately after a successful GitHub build when possible. The recurring task then handles future unattended OPRA updates.

More detail:

[`docs/AUTOMATION.md`](docs/AUTOMATION.md)

## Run locally (optional)

No third-party Python packages are required.

```bash
python src/update_docs.py
python -m unittest discover -s tests -v
python src/build_presets.py
```

You normally do not need to run this locally. GitHub Actions handles it automatically.

## Important files

- `config/targets.json` — the headphones/variants being managed.
- `src/build_presets.py` — converter logic.
- `src/update_docs.py` — automatically updates supported-headphone documentation from the config.
- `output/manifest.json` — source of truth for generated preset metadata/files.
- `docs/PROJECT_DESCRIPTION.md` — generated project-description text reflecting current configured headphones.
- `docs/ADDING_HEADPHONES.md` — beginner-friendly manual addition guide.
- `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` — reusable instructions for the ChatGPT Project.
- `docs/AUTOMATION.md` — GitHub → OPRA → Drive automation architecture.

## Attribution and licenses

The converter code in this repository is independent project code.

OPRA manufacturer, product, and EQ data is licensed by the OPRA project under CC BY-SA 4.0. Generated preset metadata is tracked in `output/manifest.json`, including the individual EQ creator and source link where OPRA provides one. See the OPRA repository for complete attribution and licensing details.

## ToneBoosters format references

The ToneBoosters/UAPP XML mapping is based on the established open-source implementations `KassMiw/PEQ2UAPP` and `SiliconExarch/EqConverter`, with independent validation and stricter error handling here.
