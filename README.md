# OPRA → UAPP ToneBoosters Preset Converter

Automatically converts selected [OPRA](https://github.com/opra-project/OPRA) parametric EQ profiles into 10-band ToneBoosters XML presets that can be imported into USB Audio Player PRO (UAPP), then mirrors the managed preset library to Google Drive.

## Project description

<!-- PROJECT_DESCRIPTION_START -->
OPRA → UAPP/ToneBoosters EQ converter v1.0.0 with automatic Google Drive sync. Configured: HIFIMAN Edition XS; SIMGOT EW300; SIMGOT EW300 Gold; SIMGOT EW300 Silver; SIMGOT EW300 DSP; Sennheiser HD650; Sony WF-1000XM5
<!-- PROJECT_DESCRIPTION_END -->

The description above is generated from `config/targets.json` and `VERSION`. The same generated text is also saved in [`docs/PROJECT_DESCRIPTION.md`](docs/PROJECT_DESCRIPTION.md) for easy copy/paste into repository or project metadata.

## Included headphones

<!-- SUPPORTED_HEADPHONES_START -->
- HIFIMAN Edition XS
- SIMGOT EW300
- SIMGOT EW300 Gold
- SIMGOT EW300 Silver
- SIMGOT EW300 DSP
- Sennheiser HD650
- Sony WF-1000XM5
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

The intended workflow is deliberately **two-stage**:

1. ChatGPT identifies the exact OPRA product, directly enumerates its real `eq/` directory, checks formatting-only aliases, and cross-checks the resulting parametric-EQ IDs against the supported `database_v1.jsonl` feed.
2. ChatGPT shows the user the verified complete candidate EQ list **before changing config**, including each proposed UAPP-visible preset name and destination folder.
3. The user explicitly chooses **Import all**, **Import only selected EQs**, or **Import all except selected EQs**. ChatGPT does not write `config/targets.json` until this approval is received.
4. If a profile cannot be classified confidently, ChatGPT asks which folder/variant it belongs to instead of guessing.
5. ChatGPT translates the approved selection into the narrowest reliable config representation.
6. GitHub Actions automatically rebuilds and validates the XML library, including profile-coverage, exact-ID selection/exclusion, route-exclusivity, and preset-naming checks.
7. GitHub Actions refreshes the README supported-headphones list and generated project description from the config.
8. ChatGPT verifies the generated manifest and UAPP-visible preset names and, when Drive write access is available, immediately syncs the new/changed XML files into the matching folder under `Google Drive / OPRA UAPP Presets`.
9. The recurring Drive sync remains a safety net for later OPRA changes.
10. You access the XML from Drive and import it into UAPP.

The reusable Project Instructions are stored here:

[`docs/CHATGPT_PROJECT_INSTRUCTIONS.md`](docs/CHATGPT_PROJECT_INSTRUCTIONS.md)

For manual additions, including copy/paste JSON examples:

[`docs/ADDING_HEADPHONES.md`](docs/ADDING_HEADPHONES.md)

## Required pre-import EQ approval

A request such as `Add the FiiO FT1` is **not** permission to immediately import every discovered profile. It starts an inventory/approval step.

Before editing config, ChatGPT must present every usable OPRA parametric EQ that would be considered for the logical headphone, across formatting-only aliases. The list should be easy to select from and should include:

- a numbered item;
- proposed UAPP-visible preset name;
- OPRA creator/author;
- OPRA details/measurement description;
- exact OPRA EQ ID;
- OPRA band count;
- proposed destination folder/variant;
- source link when OPRA supplies one.

The user can then reply in natural language, for example:

```text
Import all
Only 1, 3, and 5
All except 2 and 4
Import all except the Rtings measurement
```

For **Import all**, normal complete-coverage routing is used.

For **Import only selected EQs**, use exact `include_eq_ids` wherever practical and `allow_partial: true` so the chosen set is explicit and stable. Profiles not selected remain visible as unmatched in the manifest's intentional partial coverage report.

For **Import all except selected EQs**, use exact `exclude_eq_ids`. Explicit exclusions are recorded separately in manifest coverage and do **not** weaken the guard against accidental unmatched profiles.

Configured exact include/exclude IDs are validated against the current OPRA product. A typo or stale exact ID makes the build fail instead of silently importing/excluding the wrong thing. The same EQ ID cannot be both included and excluded in one target.

This approval checkpoint is a user-preference safeguard, separate from the converter's technical completeness checks.

## Authoritative OPRA inventory verification

GitHub search is **discovery-only**. It may help locate a product, but GitHub search results must never be used to count EQ profiles or to decide that the candidate list is complete.

Once the exact OPRA product folder is known, the required inventory source is the real directory:

`database/vendors/<vendor_id>/products/<product_folder>/eq/`

For every product record being considered, ChatGPT must:

1. directly enumerate every child folder under that exact `eq/` directory;
2. open every child's `info.json` and identify whether it is a usable `parametric_eq`;
3. repeat the same direct enumeration for formatting-only product aliases that belong to the same logical product;
4. construct the exact OPRA EQ IDs from the verified vendor/product/EQ records;
5. cross-check the complete parametric-EQ ID set and count against the supported converter feed, `https://opra.roonlabs.net/database_v1.jsonl`;
6. stop and report the discrepancy instead of showing an approval list if the repository directory and supported feed do not agree.

Before the numbered approval list, ChatGPT should state a verification summary such as:

```text
OPRA directory: 8 EQ folders
Usable parametric EQs: 8
Supported feed: the same 8 EQ IDs
```

Closely named products must also be made explicit. For example, if a user requests Sony `WF-1000XM5`, ChatGPT should state that it matched `WF-1000XM5` (in-ear) and note the separate `WH-1000XM5` (over-ear) record when relevant. This catches one-letter model mistakes without silently switching products.

If code search returns only a subset of files, that does **not** reduce the verified inventory. The directory enumeration and feed cross-check are authoritative for the approval step.

## UAPP-visible preset naming

UAPP's preset picker shows the preset's embedded ToneBoosters `Name`, but it does not show the folder that the XML came from. Presets therefore use a **headphone-first** name so the model is visible in the picker.

The standard format is:

```text
Model [Variant] - Creator - Details
```

Examples:

```text
EW300 Gold - AutoEQ - Fahryst
EW300 Silver - AutoEQ - Fahryst
EW300 DSP - AutoEQ - Jaytiss
EW300 - AutoEQ - Kazi
Edition XS - AutoEQ - Rtings
HD650 - oratory1990 - Harman Target
```

The model/variant prefix is derived from `output_path`: the manufacturer folder is omitted to save space in UAPP's narrow menu, while the model and any variant folders are retained. For example, `SIMGOT/EW300/Gold` becomes `EW300 Gold`.

For display only, redundant wording is compacted when it is safe to do so. A leading `Measured by ` is removed from OPRA details, and a trailing parenthetical variant such as `(gold)` is removed when the same variant is already present in the model prefix. **Original OPRA author/details are never changed in the manifest.**

The XML filename and the embedded ToneBoosters `PresetInfo Name` use the same generated name. `output/manifest.json` also records that value as `preset_name`, alongside the untouched OPRA `author`, `details`, IDs, and source attribution.

This naming rule is converter-level behavior. Do not manually rename generated XML files to solve UAPP display problems.

## Completeness and routing safeguards

The default policy is **complete accounting**: when a product is configured, every usable OPRA parametric EQ profile for that logical product must be imported, be an exact semantic duplicate of an imported profile, or be explicitly excluded by exact OPRA EQ ID after user approval.

The converter also treats product names that differ only by formatting as possible aliases for coverage purposes. For example, `HD650` and `HD 650` normalize to the same logical product, so profiles cannot silently disappear just because OPRA stores them under separate records.

The build fails when:

- a configured target matches no OPRA profiles;
- an OPRA parametric profile for a configured logical product is not routed, duplicate-covered, explicitly excluded, or intentionally part of a user-approved fixed subset;
- a configured `include_eq_ids` or `exclude_eq_ids` entry does not exist for that exact OPRA product;
- the same exact EQ ID is both included and excluded in one target;
- one OPRA profile is routed to multiple output folders;
- an unsupported filter type or out-of-range value is encountered.

If a user explicitly wants only a fixed subset, the target can set `"allow_partial": true`. This must be an intentional user choice, not a way to make an unexplained coverage failure green.

For a user-approved exact exclusion from an otherwise complete product, `exclude_eq_ids` records the choice without turning off future unmatched-profile detection.

For a known one-off profile that belongs in a root model folder while sibling profiles belong in variants, `include_eq_ids` can select the exact OPRA EQ ID. This is how the unclassified SIMGOT EW300 Kazi measurement is kept directly under `SIMGOT/EW300` without guessing Gold or Silver. If OPRA later adds another unclassified EW300 profile, the coverage check will fail until it is deliberately classified.

`output/manifest.json` includes a `coverage` section showing complete/partial mode, matched profile counts, duplicate-covered aliases, explicitly excluded profile IDs, and any unmatched profile IDs.

## How it works

1. Downloads OPRA's supported `database_v1.jsonl` feed.
2. Matches configured headphones using exact OPRA vendor/product metadata and explicit routing rules.
3. Audits formatting-only product aliases and validates that profiles are completely and unambiguously accounted for unless an intentional fixed subset is configured.
4. Validates configured exact include/exclude EQ IDs against the current OPRA product.
5. Generates a UAPP-visible headphone-first preset name from each configured `output_path` plus OPRA creator/details metadata.
6. Converts OPRA preamp, frequency, gain, Q, and supported filter types into ToneBoosters' normalized preset representation.
7. Writes UAPP-compatible `.xml` files under `output/`, using the same generated value for the filename and embedded preset name.
8. Writes `output/manifest.json` with generated `preset_name`, OPRA IDs, original creator/details, source links, source band counts, coverage status, explicit exclusions, and conversion warnings.
9. Regenerates the README supported-headphones section and project-description text from `config/targets.json`.
10. GitHub Actions runs the converter daily and whenever converter/config/test files change.
11. A scheduled ChatGPT task can compare GitHub output with Google Drive and mirror changed presets into the connected user's private `OPRA UAPP Presets` folder.

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
        ├── EW300 - AutoEQ - Kazi.xml
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

with UAPP-visible names beginning with:

```text
FT1 - ...
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

<!-- VERSIONING_START -->
## Versioning

Current project version: **v1.0.0**. The canonical value is stored in [`VERSION`](VERSION).

Versioning is automatic when the preset library changes:

- changing configured headphones in `config/targets.json` bumps the **minor** version;
- an OPRA update that changes generated presets without changing the configured headphone set bumps the **patch** version;
- a breaking converter change uses a **major** bump deliberately rather than automatically;
- a scheduled run with no generated changes does **not** change the version.

Each version is published as a matching Git tag such as `v1.0.0` and a GitHub Release. The release includes generated release notes, a versioned ZIP of the complete UAPP preset library, a SHA-256 checksum for that ZIP, and the matching `output/manifest.json`.

The version, supported-headphone list, and project description are regenerated by the same GitHub workflow that validates and builds the presets. Tags and releases use the normal short-lived GitHub Actions token; no personal access token is required.
<!-- VERSIONING_END -->

## Automatic updates

`.github/workflows/update-presets.yml` runs every day at 09:17 UTC and can also be started manually from the Actions tab. It also runs automatically when converter/config/test files change.

On every run, `src/update_docs.py` regenerates the supported-headphones list in this README and `docs/PROJECT_DESCRIPTION.md` from `config/targets.json` and `VERSION`. This keeps the documentation aligned even when you add a headphone manually.

The converter's coverage checks run against the current OPRA feed on every build. A newly added OPRA profile that is not covered by the existing routing rules causes a visible build failure instead of silently disappearing or being guessed into the wrong variant folder.

Preset naming is also deterministic and derived from target configuration plus OPRA metadata. Future headphone additions automatically inherit the headphone-first naming format; no per-headphone filename rules should be added.

The recurring Drive sync runs separately through ChatGPT's connected GitHub and Google Drive apps. It reads `config/targets.json` and `output/manifest.json`, so adding a new configured `output_path` does **not** require hard-coding another Drive destination.

When a headphone is added through the ChatGPT Project, the Project instructions require authoritative directory/feed inventory verification and the user EQ-selection approval checkpoint **before** config changes, then tell ChatGPT to sync the affected Drive files immediately after a successful GitHub build when possible. The recurring task then handles future unattended OPRA updates.

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

- `VERSION` — canonical Semantic Versioning value for the managed preset library.
- `config/targets.json` — the headphones/variants being managed and their explicit routing/selection rules.
- `src/build_presets.py` — converter, UAPP-visible naming, exact-ID selection/exclusion, and profile-coverage validation logic.
- `src/update_docs.py` — automatically updates supported-headphone/version documentation from the config and `VERSION`.
- `src/update_version.py` — validates and applies major/minor/patch version bumps.
- `output/manifest.json` — source of truth for generated preset filenames/names, OPRA metadata, exclusions, and coverage status.
- `docs/PROJECT_DESCRIPTION.md` — generated project-description text reflecting current configured headphones.
- `docs/ADDING_HEADPHONES.md` — beginner-friendly manual addition, approval, naming, and routing guide.
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