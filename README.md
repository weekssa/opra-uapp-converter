# OPRA → UAPP ToneBoosters Preset Converter

Automatically converts selected [OPRA](https://github.com/opra-project/OPRA) parametric EQ profiles into 10-band ToneBoosters XML presets that can be imported into USB Audio Player PRO (UAPP), then mirrors the managed preset library to Google Drive.

## Project description

<!-- PROJECT_DESCRIPTION_START -->
OPRA → UAPP/ToneBoosters EQ converter with automatic Google Drive sync. Configured: HIFIMAN Edition XS; SIMGOT EW300; SIMGOT EW300 Gold; SIMGOT EW300 Silver; SIMGOT EW300 DSP; Sennheiser HD650
<!-- PROJECT_DESCRIPTION_END -->

The description above is generated from `config/targets.json`. The same generated text is also saved in [`docs/PROJECT_DESCRIPTION.md`](docs/PROJECT_DESCRIPTION.md) for easy copy/paste into repository or project metadata.

## Included headphones

<!-- SUPPORTED_HEADPHONES_START -->
- HIFIMAN Edition XS
- SIMGOT EW300
- SIMGOT EW300 Gold
- SIMGOT EW300 Silver
- SIMGOT EW300 DSP
- Sennheiser HD650
<!-- SUPPORTED_HEADPHONES_END -->

This list is generated automatically from `config/targets.json`, so adding or removing a target updates the documentation on the next GitHub build.

## Use your own fork and private Drive

This project is designed so another user can fork the repository, connect ChatGPT to **their own fork** and **their own Google Drive**, and maintain a completely independent preset library.

The Google Drive folder does **not** need to be public or shared with GitHub. No Google credentials are stored in this repository.

Start here:

[`docs/NEW_USER_SETUP.md`](docs/NEW_USER_SETUP.md)

That guide covers:

1. forking the public repository;
2. enabling GitHub Actions in the fork;
3. authorizing ChatGPT to access the user's fork;
4. connecting the user's own Google Drive with the required Drive actions;
5. creating a private `OPRA UAPP Presets` Drive folder;
6. configuring a ChatGPT Project for the fork;
7. optionally setting up recurring Drive synchronization.

# The easy way to add a headphone

Use the ChatGPT Project connected to this repository and say:

> Add the FiiO FT1 to my OPRA UAPP presets.

The intended workflow is:

1. ChatGPT checks current OPRA data for the exact headphone, formatting-only product aliases, available parametric EQ profiles, and identifiable variants.
2. Every usable OPRA parametric profile is accounted for by the proposed routing. If a profile cannot be classified confidently, ChatGPT asks which folder/subset you want instead of guessing.
3. ChatGPT updates `config/targets.json`.
4. GitHub Actions automatically rebuilds and validates the XML library, including profile-coverage and overlapping-route checks.
5. GitHub Actions refreshes the README supported-headphones list and generated project description from the config.
6. ChatGPT verifies the generated manifest and, when Drive write access is available, immediately syncs the new/changed XML files into the matching folder under `Google Drive / OPRA UAPP Presets`.
7. The recurring Drive sync remains a safety net for later OPRA changes.
8. You access the XML from Drive and import it into UAPP.

The reusable Project Instructions are stored here:

[`docs/CHATGPT_PROJECT_INSTRUCTIONS.md`](docs/CHATGPT_PROJECT_INSTRUCTIONS.md)

For manual additions, including copy/paste JSON examples:

[`docs/ADDING_HEADPHONES.md`](docs/ADDING_HEADPHONES.md)

## Completeness and routing safeguards

The default policy is **complete coverage**: when a product is configured, every usable OPRA parametric EQ profile for that logical product must either be imported or be an exact semantic duplicate of an imported profile.

The converter also treats product names that differ only by formatting as possible aliases for coverage purposes. For example, `HD650` and `HD 650` normalize to the same logical product, so profiles cannot silently disappear just because OPRA stores them under separate records.

The build fails when:

- a configured target matches no OPRA profiles;
- an OPRA parametric profile for a configured logical product is not routed anywhere;
- one OPRA profile is routed to multiple output folders;
- an unsupported filter type or out-of-range value is encountered.

If a user explicitly wants only a subset, the target can set `"allow_partial": true`. This must be an intentional user choice, not a way to make an unexplained coverage failure green.

For a known one-off profile that belongs in a root model folder while sibling profiles belong in variants, `include_eq_ids` can select the exact OPRA EQ ID. This is how the unclassified SIMGOT EW300 Kazi measurement is kept directly under `SIMGOT/EW300` without guessing Gold or Silver. If OPRA later adds another unclassified EW300 profile, the coverage check will fail until it is deliberately classified.

`output/manifest.json` includes a `coverage` section showing complete/partial mode, matched profile counts, duplicate-covered aliases, and any unmatched profile IDs.

## How it works

1. Downloads OPRA's supported `database_v1.jsonl` feed.
2. Matches configured headphones using exact OPRA vendor/product metadata and explicit routing rules.
3. Audits formatting-only product aliases and validates that profiles are completely and unambiguously routed unless an intentional partial import is configured.
4. Converts OPRA preamp, frequency, gain, Q, and supported filter types into ToneBoosters' normalized preset representation.
5. Writes UAPP-compatible `.xml` files under `output/`.
6. Writes `output/manifest.json` with OPRA IDs, creator attribution, source links, source band counts, coverage status, and any conversion warnings.
7. Regenerates the README supported-headphones section and project-description text from `config/targets.json`.
8. GitHub Actions runs the converter daily and whenever converter/config/test files change.
9. A scheduled ChatGPT task can compare GitHub output with Google Drive and mirror changed presets into the connected user's private `OPRA UAPP Presets` folder.

## Output folders

Current output:

```text
output/
├── HIFIMAN/
│   └── Edition XS/
├── Sennheiser/
│   └── HD650/
└── SIMGOT/
    └── EW300/
        ├── AutoEQ - Measured by Kazi.xml
        ├── Gold/
        ├── Silver/
        └── DSP/
```

New folders come directly from each target's `output_path` in `config/targets.json`. A model root can contain XML files directly while also containing variant subfolders.

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

Only use a real OPRA `vendor_id`, exact OPRA product name, and verified EQ IDs/variant terms. See the adding-headphones guide for the routing rules.

## UAPP / ToneBoosters behavior

UAPP's ToneBoosters preset format is a 10-band format. OPRA explicitly prioritizes its band list for software with limited band counts, so if an OPRA preset ever contains more than 10 bands this converter uses the first 10 and records a warning in the manifest.

The current converter intentionally supports:

- Peak / dip
- Low shelf
- High shelf

If OPRA later supplies an unsupported filter type for one of the configured targets, generation fails instead of silently producing an incorrect preset.

## Automatic updates

`.github/workflows/update-presets.yml` runs every day at 09:17 UTC and can also be started manually from the Actions tab. It also runs automatically when converter/config/test files change.

On every run, `src/update_docs.py` regenerates the supported-headphones list in this README and `docs/PROJECT_DESCRIPTION.md` from `config/targets.json`. This keeps the documentation aligned even when you add a headphone manually.

The converter's coverage checks run against the current OPRA feed on every build. A newly added OPRA profile that is not covered by the existing routing rules causes a visible build failure instead of silently disappearing or being guessed into the wrong variant folder.

The recurring Drive sync runs separately through ChatGPT's connected GitHub and Google Drive apps. It reads `config/targets.json` and `output/manifest.json`, so adding a new configured `output_path` does **not** require hard-coding another Drive destination.

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

- `config/targets.json` — the headphones/variants being managed and their explicit routing rules.
- `src/build_presets.py` — converter and profile-coverage validation logic.
- `src/update_docs.py` — automatically updates supported-headphone documentation from the config.
- `output/manifest.json` — source of truth for generated preset metadata/files and coverage status.
- `docs/PROJECT_DESCRIPTION.md` — generated project-description text reflecting current configured headphones.
- `docs/ADDING_HEADPHONES.md` — beginner-friendly manual addition and routing guide.
- `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` — reusable instructions for a ChatGPT Project.
- `docs/NEW_USER_SETUP.md` — setup guide for a user's own fork and private Google Drive.
- `docs/AUTOMATION.md` — GitHub → OPRA → Drive automation architecture.
- `LICENSE` — Apache License 2.0 for the converter software/documentation.
- `NOTICE` — third-party software provenance/attribution.
- `DATA_LICENSE.md` — licensing/attribution rules for OPRA-derived output.

## Attribution and licenses

The converter software and project documentation are distributed under the **Apache License, Version 2.0**. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

The ToneBoosters/UAPP normalization and XML mapping is based in part on `SiliconExarch/EqConverter`, which is Apache-2.0 licensed. This repository substantially rewrites and extends that work for OPRA ingestion, validation, additional supported filter types, deterministic generation, attribution metadata, documentation, and Drive-oriented maintenance.

OPRA manufacturer, product, and EQ data is licensed by the OPRA project under **CC BY-SA 4.0**. The OPRA-derived portions of generated files under `output/` are therefore not covered by the repository's Apache-2.0 software license. Creator attribution, source links, and OPRA identifiers are preserved in `output/manifest.json`.

See [`DATA_LICENSE.md`](DATA_LICENSE.md) for the software/data licensing boundary and attribution details.

## ToneBoosters format provenance

The original normalization/XML serialization reference used by this converter is `SiliconExarch/EqConverter` (Apache-2.0). Other publicly available community converters may be used only as compatibility cross-checks; their source is not redistributed here unless explicitly identified and licensed.
