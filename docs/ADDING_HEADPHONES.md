# Adding headphones

This project is designed so normal headphone additions require editing only one file:

`config/targets.json`

You do **not** need to change the converter code for a normal OPRA headphone addition.

If you are using your own public fork, complete [`NEW_USER_SETUP.md`](NEW_USER_SETUP.md) first so GitHub Actions is enabled for your fork and ChatGPT is connected to your own GitHub repository and Google Drive.

## Easiest method: ask the ChatGPT Project

In the ChatGPT Project for this repository, use a request like:

> Add the FiiO FT1 to my OPRA UAPP converter.

The request starts an inventory/approval workflow. ChatGPT should **not** immediately edit `config/targets.json`.

ChatGPT should:

1. Inspect OPRA for the exact product.
2. Check the same vendor for near-duplicate product records whose names differ only by spaces, punctuation, hyphens, capitalization, or similar formatting.
3. Inventory **every usable parametric EQ profile** across those formatting-only aliases.
4. Identify meaningful variants from OPRA IDs/details/metadata. Never infer a variant that OPRA does not identify.
5. Build the proposed routing and generated UAPP-visible name for every candidate EQ.
6. Present the complete candidate list to the user **before any config change**.
7. Ask the user to choose one of these outcomes:
   - **Import all**
   - **Import only selected EQs**
   - **Import all except selected EQs**
8. If a profile cannot be confidently assigned to a folder/variant, ask the user where they want it instead of guessing.
9. Only after the user approves the profile selection, read/update `config/targets.json` using the narrowest reliable rules.
10. Let GitHub Actions rebuild the preset library.
11. Verify the workflow succeeded and inspect both the generated presets and the manifest `coverage` section.
12. Verify each generated `preset_name` starts with the expected headphone/model and variant and follows the standard UAPP-visible naming format.
13. Confirm there are no unexplained unmatched profiles or overlapping routes and that any explicit exclusions match the user's approval.
14. If Google Drive write actions are connected, immediately mirror the new/changed Drive files and update the Drive root `manifest.json`.
15. Leave the recurring Drive sync as a safety net for later OPRA changes.

If OPRA does not contain a usable parametric EQ for the headphone, ChatGPT should tell you instead of inventing one.

---

# Required user approval before import

Before config is edited, ChatGPT should show a numbered list of **all usable OPRA parametric EQs** being considered for the logical headphone.

For each item, show enough information for the user to recognize what they are approving:

- proposed UAPP-visible name;
- OPRA creator/author;
- OPRA details/measurement description;
- exact OPRA EQ ID;
- OPRA band count;
- proposed destination folder/variant;
- source link when OPRA provides one.

A compact example:

```text
1. FT1 - AutoEQ - Measurement Lab A
   OPRA ID: fiio:ft1::autoeq_lab_a
   Bands: 10
   Folder: FiiO/FT1

2. FT1 - oratory1990 - Harman Target
   OPRA ID: fiio:ft1::oratory1990_harman_target
   Bands: 10
   Folder: FiiO/FT1
```

The user can reply naturally, for example:

```text
Import all
Only 1 and 2
All except 2
Import everything except the Rtings profile
```

ChatGPT should resolve the response to exact OPRA EQ IDs and state the resulting selection clearly before writing config. The original `Add [headphone]` request alone is not the approval to import every profile.

This checkpoint is for user preference/expectation. It is separate from the technical coverage checks that protect against accidental omissions.

# Manual method

## 1. Find the headphone in OPRA

Open the OPRA repository:

`https://github.com/opra-project/OPRA`

Search for the headphone model.

The maintained product files live under paths shaped like:

`database/vendors/<vendor_id>/products/<product_folder>/info.json`

You need two values:

- `vendor_id`: the folder name directly under `database/vendors/`
- `product_name`: the exact `name` value in the product's `info.json`

Example for Edition XS:

- Vendor folder: `hifiman`
- Product name: `Edition XS`

### Important: check formatting-only aliases

Do not stop after finding the first similar-looking product name. OPRA can contain separate records whose names differ only by formatting.

For example, OPRA currently contains both `HD650` and `HD 650` under Sennheiser. They expose different profile sets. The converter therefore treats names that normalize to the same letters/numbers as one logical product for **coverage validation**.

That does not mean every similar name is automatically the same physical product. If two records normalize together but you cannot determine whether they should be combined, stop and ask the user rather than guessing.

## 2. Inventory and approve the complete profile set

Before writing config, list all usable `parametric_eq` entries for the logical product and note:

- exact OPRA EQ ID;
- author;
- details/measurement text;
- band count;
- proposed UAPP-visible name;
- proposed destination folder;
- source link if available;
- whether the profile identifies a variant such as Gold/Silver, pad condition, nozzle, revision, or other tuning distinction;
- whether an apparently duplicated profile is actually identical to one in another formatting-only alias.

Then decide which profiles are approved for import.

The default **technical** goal is complete accounting, but the user's preference controls the actual imported set. Every usable profile must end up in one of these states:

- imported;
- exact semantic duplicate of an imported profile;
- explicitly excluded by the user;
- intentionally outside a fixed selected subset.

## 3. Edit `config/targets.json`

### Simple product: import everything together

After the user approves **Import all**:

```json
{
  "vendor_id": "hifiman",
  "product_name": "Edition XS",
  "output_path": "HIFIMAN/Edition XS"
}
```

When there are no filters, every parametric EQ for that exact OPRA product record is selected.

### Identifiable variants

Use `include_terms` when OPRA itself clearly identifies variants in EQ IDs, author text, or details:

```json
{
  "vendor_id": "simgot_audio",
  "product_name": "EW300",
  "include_terms": ["gold"],
  "output_path": "SIMGOT/EW300/Gold"
},
{
  "vendor_id": "simgot_audio",
  "product_name": "EW300",
  "include_terms": ["silver"],
  "output_path": "SIMGOT/EW300/Silver"
}
```

Variant rules must be mutually exclusive. If one OPRA profile matches multiple output folders, the build fails rather than duplicating it silently.

### Known one-off profile in the model root

Use `include_eq_ids` when a specific known profile belongs directly in the model root while sibling profiles are split into variants:

```json
{
  "vendor_id": "simgot_audio",
  "product_name": "EW300",
  "include_eq_ids": ["simgot_audio:ew300::autoeq_kazi"],
  "output_path": "SIMGOT/EW300"
}
```

This is intentionally narrow. If OPRA later adds another unclassified EW300 profile, that new profile will **not** be silently dumped into the root. The coverage check will fail until someone decides where it belongs.

### User chose only specific EQs

When the user says **Import only selected EQs**, prefer exact `include_eq_ids` so the approved set is unambiguous and stable:

```json
{
  "vendor_id": "example",
  "product_name": "Model",
  "include_eq_ids": [
    "example:model::profile_one",
    "example:model::profile_three"
  ],
  "allow_partial": true,
  "output_path": "Example/Model"
}
```

This intentionally freezes that target to the selected exact IDs. Other current or future profiles are not automatically imported until the user revisits the selection.

### User chose all except specific EQs

When the user says **Import all except selected EQs**, use exact `exclude_eq_ids`:

```json
{
  "vendor_id": "example",
  "product_name": "Model",
  "exclude_eq_ids": [
    "example:model::profile_two"
  ],
  "output_path": "Example/Model"
}
```

This keeps the product in normal complete-accounting mode while recording the user's exact exclusion. Other profiles still import normally, including future profiles that match the same route.

The converter verifies each configured exact include/exclude ID exists for that exact OPRA product. A typo or stale ID fails the build rather than silently changing the user's selection.

### Intentional variant subset

If the user explicitly asks for only a broad identifiable variant rather than individual EQs, `include_terms` plus `allow_partial` can still be appropriate:

```json
{
  "vendor_id": "example",
  "product_name": "Model",
  "include_terms": ["red"],
  "allow_partial": true,
  "output_path": "Example/Model/Red"
}
```

Use `allow_partial` only for a deliberate subset request. Do **not** add it merely to bypass an unexplained coverage error.

### Config field reference

- `vendor_id`: exact OPRA vendor id.
- `product_name`: exact OPRA product name for this target entry.
- `output_path`: relative GitHub/Drive folder and source of the UAPP-visible model/variant prefix.
- `include_terms`: optional case-insensitive substring filters against OPRA EQ id, author, and details.
- `include_eq_ids`: optional exact OPRA EQ IDs for precise routing or a fixed user-selected subset.
- `exclude_eq_ids`: optional exact OPRA EQ IDs the user explicitly chose not to import from an otherwise matching target.
- `allow_partial`: optional boolean. Default `false`; when `true`, unmatched profiles for that logical product are allowed because the user intentionally requested a subset.

An exact EQ ID must not appear in both `include_eq_ids` and `exclude_eq_ids` for the same target.

## 4. Understand UAPP-visible preset naming

UAPP does not show the source folder in its preset picker, so the converter puts the headphone first in every generated preset name.

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

The prefix comes from `output_path` with the first manufacturer component removed:

- `HIFIMAN/Edition XS` → `Edition XS`
- `SIMGOT/EW300` → `EW300`
- `SIMGOT/EW300/Gold` → `EW300 Gold`
- `SIMGOT/EW300/DSP` → `EW300 DSP`

The converter uses that same generated string for both the XML filename and the embedded ToneBoosters preset `Name`.

For readability, display-only details may remove a leading `Measured by ` and may remove a trailing parenthetical variant when it simply repeats the configured variant. For example, OPRA author/details `AutoEQ` + `Measured by Fahryst (gold)` become:

```text
EW300 Gold - AutoEQ - Fahryst
```

This cleanup is **display only**. The original OPRA `author` and `details` remain unchanged in `output/manifest.json`, along with the generated `preset_name` field.

Do not add manual filename overrides for normal headphones. Choose a clean `output_path`; the converter should generate the UAPP-visible name automatically.

## 5. Understand the automatic coverage checks

For every configured logical product, the converter:

1. normalizes formatting-only product names (spaces/punctuation/case) to discover possible aliases;
2. gathers every parametric EQ across those aliases;
3. checks which EQs are routed by the config;
4. validates configured exact `include_eq_ids` and `exclude_eq_ids` against the exact OPRA product;
5. records exact user-approved exclusions separately as `explicitly_excluded_profiles`;
6. treats an unmatched alias EQ as covered only when its author/details/filter parameters are semantically identical to an imported EQ;
7. fails if any non-duplicate, non-excluded EQ is left unmatched unless the logical product is explicitly partial;
8. fails if one EQ is routed to multiple different output folders.

This safeguard is what prevents the original `HD650` / `HD 650` type of omission from happening silently again while still respecting the user's explicit import preferences.

## 6. Save the config and check the build

When `config/targets.json` changes on `main`, the `Update OPRA presets` GitHub Action runs automatically after Actions has been enabled for that repository/fork.

It will:

1. regenerate documentation;
2. run converter tests, including the headphone-first preset-name and exact selection/exclusion tests;
3. download the current OPRA database;
4. validate target matching, exact include/exclude IDs, logical-product coverage, duplicate aliases, and overlapping routes;
5. generate the XML library;
6. update `output/manifest.json` and XML files only when actual output changed.

A red coverage or exact-ID failure is a request to investigate the selection/routing, not permission to weaken validation.

## 7. Inspect `output/manifest.json`

The manifest shows per-preset metadata plus a top-level `coverage` section.

For each generated preset, verify:

- `file`: generated path/filename;
- `preset_name`: exact name UAPP will show;
- `author` and `details`: original OPRA values, unchanged;
- OPRA EQ/product IDs and source attribution.

For each logical product, check:

- `mode`: `complete` or `partial`;
- `opra_parametric_profiles`;
- `matched_profiles`;
- `duplicate_profiles_covered`;
- `explicitly_excluded_profiles`;
- `unmatched_profiles`.

For **Import all**, `explicitly_excluded_profiles` and `unmatched_profiles` should normally both be empty.

For **Import all except selected**, `explicitly_excluded_profiles` must exactly match the user's approved exclusions and `unmatched_profiles` must be empty.

For **Import only selected**, `mode` should be `partial`, generated entries should exactly match the approved IDs, and the non-selected profiles remain visible in `unmatched_profiles` as intentional partial coverage.

Also verify the generated `preset_name` begins with the expected model/variant rather than only the creator name.

## 8. Google Drive sync

GitHub does not receive your Google credentials and does not directly write to Drive.

When ChatGPT has Google Drive write actions connected, it mirrors generated files under:

`Google Drive / OPRA UAPP Presets /`

A model root can contain XML files directly while also containing managed variant subfolders. For example:

```text
OPRA UAPP Presets/
└── SIMGOT/
    └── EW300/
        ├── EW300 - AutoEQ - Kazi.xml
        ├── Gold/
        ├── Silver/
        └── DSP/
```

The sync adds/updates generated XML files, removes obsolete generated XML files only within managed locations, preserves unrelated Drive content, and updates the root `manifest.json`.

When naming behavior changes, treat the old filename as obsolete generated output and the new headphone-first filename as its replacement. Do not leave both versions in Drive.

## Removing a headphone

Delete the applicable target object(s) from `config/targets.json` and save the change.

If multiple entries represent aliases or variants of one model, remove the whole intended logical set unless you specifically want to keep a subset. Rebuild first, then mirror the resulting managed changes to Drive.

## Important rules

- Never invent OPRA product names, IDs, variants, or EQ profiles.
- Always inventory formatting-only OPRA aliases before selecting targets.
- **Never edit config for a new headphone until the user has seen the full candidate EQ list and approved the import set.**
- Complete accounting is the technical default, but the user's approved selection controls which EQs are imported.
- Ask the user when classification is genuinely ambiguous; do not guess a folder.
- Use exact `include_eq_ids` for fixed user-selected EQ sets or one-off routing when that is safer than a broad text filter.
- Use exact `exclude_eq_ids` for explicit user exclusions from an otherwise matching target.
- Never invent or silently correct an exact EQ ID; the build validates it against OPRA.
- Use `allow_partial` only when the user explicitly requests a subset.
- Never weaken coverage validation merely to make a build green.
- Keep the UAPP-visible naming rule `Model [Variant] - Creator - Details`; do not regress to creator-only names.
- Preserve original OPRA author/details/source metadata even when display-only naming removes redundant wording.
- Never manually edit or rename generated XML files as the normal workflow.
- Preserve OPRA and individual EQ creator attribution.
- Do not silently drop unsupported filter types.
- UAPP/ToneBoosters is limited to 10 bands in this converter. If OPRA provides more, OPRA's priority order is used and the manifest records a warning.
- Never commit Google OAuth tokens, service-account keys, GitHub personal access tokens, or other credentials to this repository.