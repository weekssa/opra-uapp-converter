# ChatGPT Maintenance Runbook

This is the detailed behavioral source of truth for ChatGPT installations of the OPRA → UAPP/ToneBoosters converter. It is **not** intended to be pasted into the ChatGPT Project Instructions field. That field has a practical length limit; paste `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` there instead. The paste-ready bootstrap requires ChatGPT to read this runbook from the connected repository before OPRA maintenance work.

For a fork, the repository is the one named in the user's Project Instructions. The default Drive root is `OPRA UAPP Presets`.

## Project goal

Maintain a reliable, automatically updated library of selected OPRA parametric EQ profiles converted to UAPP/ToneBoosters XML presets and mirrored into the user's private Google Drive.

The user may be a non-developer. Perform GitHub inspection, config editing, validation, documentation, and Drive work through connected tools whenever available. Give manual steps only for actions that truly require the user.

Primary OPRA source:
`https://github.com/opra-project/OPRA`

Supported distribution feed used by the converter:
`https://opra.roonlabs.net/database_v1.jsonl`

## Security and account boundaries

- Treat GitHub and Google Drive as separate user-authorized connections.
- Never request or commit OAuth tokens, service-account keys, passwords, ChatGPT credentials, GitHub PATs, or other secrets.
- Drive may remain private; it does not need to be shared with GitHub.
- Operate only on the repository named in Project Instructions and the connected user's `OPRA UAPP Presets` folder.
- If a needed write action is unavailable, explain the smallest manual step instead of asking for credentials.

## Repository files to inspect

For normal maintenance, inspect the current repository state, especially:
- `README.md`
- `config/targets.json`
- `docs/ADDING_HEADPHONES.md`
- `docs/AUTOMATION.md`
- `docs/PROJECT_DESCRIPTION.md`
- `output/manifest.json`

This runbook and those files are live sources. Do not substitute remembered copies for current GitHub content.

# New-headphone workflow

A request such as `Add the FiiO FT1` has two phases. **The first message is not permission to import all discovered EQs.**

## Phase 1 — authoritative discovery and user approval

### 1. Identify the exact OPRA product

Use search only to locate likely products. **GitHub search is discovery-only.** Never use code-search hits to count EQs or decide that an inventory is complete.

Read the exact product `info.json` and record:
- vendor id;
- OPRA product name;
- OPRA product folder;
- type/subtype.

Never invent or silently repair a product identity.

### 2. Similar-product safeguard

Inspect the same vendor for closely named siblings that could be confused with the request. Explicitly mention meaningful near-matches before the EQ list.

Examples of distinctions that must not be silently collapsed:
- WF vs WH;
- wired vs wireless;
- ANC on/off;
- DSP vs non-DSP;
- revision/model-number differences;
- eartip, pad, nozzle, filter, or other hardware variants.

A typo may be resolved to an obvious candidate only when the response clearly states the exact product chosen and meaningful alternatives. If the intended product is genuinely ambiguous, ask before proceeding.

### 3. Enumerate the actual OPRA EQ directory

Once the exact product folder is known, directly enumerate:

`database/vendors/<vendor_id>/products/<product_folder>/eq/`

List every child folder. Open **every child's `info.json`**. Every entry with `type: parametric_eq` is a usable candidate for this converter.

Do not infer the number of EQs from:
- GitHub search results;
- a few known creators;
- stale prior manifests;
- memory;
- product-name search snippets.

If formatting-only OPRA product aliases may represent the same logical product (spaces, punctuation, hyphens, capitalization, etc.), directly enumerate those alias `eq/` directories too.

### 4. Cross-check the supported feed

Construct the exact OPRA EQ IDs for all usable candidates and cross-check the exact set and count against:

`https://opra.roonlabs.net/database_v1.jsonl`

The approval inventory is valid only when the repository directory and supported feed agree for the logical product.

If they disagree:
- stop before config edits;
- do not choose whichever source returned fewer profiles;
- report exact repository-only/feed-only IDs and counts;
- investigate the discrepancy before asking for import approval.

### 5. Determine routing without guessing

For every verified profile, propose the narrowest defensible destination based only on OPRA metadata/IDs/details:
- `Manufacturer/Model`
- or `Manufacturer/Model/Variant`.

Use a root route when all profiles belong together. Use variant folders only when OPRA provides a reliable distinction. If folder/variant meaning is ambiguous, show the ambiguity to the user rather than guessing.

Exact semantic duplicates across formatting-only aliases may be represented once, preferring the record with richer attribution/source metadata, but duplicate accounting must remain explainable.

### 6. Preview UAPP-visible names

Every generated preset must identify the headphone because UAPP may show only the embedded preset name, not its folder.

Format:

`Model [Variant] - Creator - Details`

Examples:
- `EW300 Gold - AutoEQ - Fahryst`
- `EW300 DSP - AutoEQ - Jaytiss`
- `EW300 - AutoEQ - Kazi`
- `Edition XS - AutoEQ - Rtings`
- `HD650 - oratory1990 - Harman Target`

The model/variant prefix comes from `output_path` with the manufacturer component removed.

Display-only compaction may remove a leading `Measured by ` and a trailing parenthetical variant that merely repeats the configured variant. Original OPRA author/details/source metadata must remain unchanged in the manifest.

### 7. Show the verified approval inventory

Before the numbered list, state a short verification summary containing:
- exact matched product and subtype;
- OPRA directory EQ-folder count;
- usable parametric-EQ count;
- feed cross-check result.

Example:

```text
Matched product: Sony WF-1000XM5 (in-ear)
OPRA directory: 8 EQ folders
Usable parametric EQs: 8
Supported database_v1.jsonl feed: the same 8 EQ IDs
```

For each candidate, show:
1. simple selection number;
2. proposed UAPP-visible name;
3. OPRA creator/author;
4. original OPRA details;
5. exact OPRA EQ ID;
6. band count;
7. proposed `output_path`/variant;
8. source link when OPRA provides one.

If two records currently have identical EQ parameters but OPRA exposes them as separate profiles with different metadata/targets, show both unless the converter's semantic-duplicate logic specifically covers them. Do not silently hide a candidate merely because parameters look identical.

### 8. Require explicit user selection

Offer:
- **Import all**
- **Import only selected EQs**
- **Import all except selected EQs**

Accept natural language such as:
- `all`
- `only 1, 3 and 5`
- `all except 2`
- `everything except Rtings`

Resolve the choice to exact OPRA EQ IDs.

If the initial request already specified a subset or variant, still inventory the full relevant logical product, show selected and unselected profiles, and ask for confirmation.

**Stop before editing `config/targets.json` and wait for approval.**

If OPRA contains no usable parametric EQ, say so and stop.

## Phase 2 — apply exactly what the user approved

### Config representation

For a normal headphone addition, edit only `config/targets.json` unless the current converter genuinely cannot represent the approved selection.

Use:
- no filtering fields for **Import all** when all profiles for that exact product record belong together;
- `include_terms` for OPRA-identifiable variants;
- `include_eq_ids` for exact one-off routing or a fixed **only selected** set;
- `exclude_eq_ids` for **all except selected**;
- `allow_partial: true` only for an intentionally fixed/broad subset.

For **only selected**, prefer exact `include_eq_ids` plus `allow_partial: true`; future profiles remain outside the fixed approved set until the user changes it.

For **all except selected**, use exact `exclude_eq_ids` on otherwise complete routing. Do **not** use `allow_partial` merely to implement exclusions. Future unrelated matching profiles should still be discoverable/importable.

Validate every configured exact include/exclude ID against the current OPRA parametric-EQ IDs for the exact target product. A stale, mistyped, or conflicting ID is a failure to investigate, not something to silently correct.

The same EQ ID must never be both included and excluded in one target.

Never weaken coverage or add `allow_partial` merely to hide an unexplained unmatched profile.

Never create overlapping target rules that route one OPRA EQ to multiple output folders.

### Complete accounting

For a normally managed logical product, every usable profile must be accounted for as:
- imported;
- exact semantic duplicate of an imported profile;
- explicitly excluded by user-approved exact ID;
- intentionally outside a fixed user-selected subset.

The converter's build-time logical-product coverage and overlap checks are a second line of defense. They do not replace the pre-import inventory gate.

### Build and documentation validation

After changing config:
1. verify GitHub Action `Update OPRA presets` runs successfully;
2. verify it runs `src/update_docs.py`;
3. confirm README supported-headphones/generated-description sections and `docs/PROJECT_DESCRIPTION.md` are regenerated from config;
4. do not hand-edit generated `docs/PROJECT_DESCRIPTION.md`.

Inspect `output/manifest.json` and confirm:
- expected preset count/files;
- creator, original details, source attribution;
- `preset_name` begins with correct model/variant;
- file stem and embedded XML Name match `preset_name`;
- matched profiles correspond to the approved import set;
- `explicitly_excluded_profiles` exactly match all-except choices;
- partial coverage mode appears only for intentional subset behavior;
- complete products have no unexplained `unmatched_profiles`;
- duplicate-covered profiles are explainable;
- warnings are expected;
- manifest errors are empty.

If build/coverage/routing/naming/selection validation fails, fix the actual cause. Never weaken validation merely to make CI green.

### Drive sync after successful build

If connected Drive write actions are available, immediately mirror the new/changed/renamed generated XML files to the matching relative paths beneath:

`OPRA UAPP Presets`

Create missing folders. Update the Drive root `manifest.json`.

When a generated preset is renamed, replace/rename safely so obsolete generated filenames do not remain as duplicate UAPP presets.

A model root may contain XMLs directly plus variant child folders. Delete/replace only managed generated XMLs at the applicable folder level; do not recursively remove unrelated child folders/content.

Drive is a mirror, not a second source of truth. Preserve unrelated Drive content.

The recurring Drive sync is only a safety net for later OPRA changes.

# Converter safety rules

- Never silently change EQ values.
- Preserve OPRA preamp, frequency, gain, Q, band priority, author, details, and source attribution.
- Do not manually edit generated XML as the normal solution.
- Do not silently ignore unsupported OPRA filter types.
- UAPP/ToneBoosters output is limited to 10 bands. If OPRA has more than 10, preserve priority order, use the first 10, and keep the manifest warning.
- Keep distinct 5-band and 10-band versions when OPRA contains both.
- Keep output deterministic so unchanged source data does not create unnecessary commits.
- Keep XML/preset names ISO-8859-1-safe while retaining full original OPRA metadata in the UTF-8 manifest.
- XML filename, embedded ToneBoosters PresetInfo Name, and manifest `preset_name` must agree.

# Later OPRA changes

When OPRA adds profiles to a configured product:
- complete/all-except routing may automatically accept a new profile only when existing routing unambiguously covers it and it is not an exact exclusion;
- exact exclusions apply only to the IDs the user declined;
- fixed `include_eq_ids` subsets remain fixed until the user changes them;
- a new profile that falls through complete routing must not be silently ignored;
- overlapping/ambiguous new routing must be investigated;
- if primary repository and supported feed may have diverged, compare the exact product `eq/` directory with `database_v1.jsonl` before config changes;
- new generated names must automatically follow the headphone-first naming rule.

# Remove headphone

For `Remove [headphone]`:
1. inspect current target(s) and managed outputs;
2. remove the intended config target(s);
3. rebuild safely;
4. confirm generated documentation is updated;
5. validate manifest/coverage;
6. remove only the corresponding managed generated files/folders from Drive when possible;
7. preserve unrelated content and explain what changed.

# Check for new presets

For `Check for new presets`:
- inspect latest OPRA/build state;
- compare exact primary-directory/feed state if coverage suggests a discrepancy;
- respect fixed subsets and exact exclusions;
- if new profiles fit complete routing, validate generated names/output and sync;
- if classification is ambiguous, ask the user rather than guessing.

# Drive commands

For `Sync Drive now` or `Is Drive up to date?`:
- read current `config/targets.json` and `output/manifest.json`;
- verify latest relevant build/manifest health;
- respect selection/exclusion state;
- compare managed GitHub output to the user's connected `OPRA UAPP Presets`;
- mirror additions/updates/renames/removals safely;
- update the Drive root manifest;
- do nothing when already current.

# Generated project description

`docs/PROJECT_DESCRIPTION.md` is generated from `config/targets.json` and is canonical for repository description text. When repository metadata write capability exists, keep the visible GitHub About/Description consistent. If metadata write is unavailable, keep the generated file current; require manual paste only if the user actually needs the visible metadata changed.

# Documentation maintenance

Whenever configured headphones change, keep these synchronized via the repository tooling:
- README supported-headphones list;
- README generated project-description section;
- `docs/PROJECT_DESCRIPTION.md`.

When behavior changes, update relevant docs:
- `README.md`
- `docs/ADDING_HEADPHONES.md`
- `docs/AUTOMATION.md`
- `docs/CHATGPT_PROJECT_INSTRUCTIONS.md`
- this `docs/CHATGPT_MAINTENANCE_RUNBOOK.md`
- `docs/NEW_USER_SETUP.md` when setup/new-user expectations change.

`docs/CHATGPT_PROJECT_INSTRUCTIONS.md` must remain paste-ready for ChatGPT Project settings and safely below the UI's instruction-length limit. Keep detailed rules here rather than growing the paste-ready bootstrap indefinitely.

# Communication style

Be concise and step-by-step. State what changed and whether validation passed. Use connected GitHub/Drive tools instead of giving Terminal/Git/Python instructions when possible. For a new headphone, make the verified candidate list easy to scan. Ask only for genuine product/folder/EQ-selection ambiguity; otherwise complete the work directly.
