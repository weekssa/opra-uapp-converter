# Adding headphones

This project is designed so normal headphone additions require editing only one file:

`config/targets.json`

You do **not** need to change the converter code for a normal OPRA headphone addition.

If you are using your own public fork, complete [`NEW_USER_SETUP.md`](NEW_USER_SETUP.md) first so GitHub Actions is enabled for your fork and ChatGPT is connected to your own GitHub repository and Google Drive.

## Easiest method: ask the ChatGPT Project

In the ChatGPT Project for this repository, use a request like:

> Add the FiiO FT1 to my OPRA UAPP converter. Find the exact current OPRA vendor/product information, account for every usable parametric EQ profile, update `config/targets.json`, verify the GitHub Action succeeds, and confirm which UAPP XML presets were generated. If a profile or variant cannot be classified confidently, ask me instead of guessing.

ChatGPT should:

1. Inspect OPRA for the exact product.
2. Check the same vendor for near-duplicate product records whose names differ only by spaces, punctuation, hyphens, capitalization, or similar formatting.
3. Inventory **every usable parametric EQ profile** across those formatting-only aliases.
4. Identify meaningful variants from OPRA IDs/details/metadata. Never infer a variant that OPRA does not identify.
5. Decide whether all profiles belong together, should be split into variant folders, or require a user choice.
6. If a profile cannot be confidently assigned, ask the user where they want it rather than placing it in a guessed folder.
7. Read the current `config/targets.json` first and add the smallest necessary target entries.
8. Let GitHub Actions rebuild the preset library.
9. Verify the workflow succeeded and inspect both the generated presets and the manifest `coverage` section.
10. Confirm there are no unexplained unmatched profiles or overlapping routes.
11. If Google Drive write actions are connected, immediately mirror the new/changed Drive files and update the Drive root `manifest.json`.
12. Leave the recurring Drive sync as a safety net for later OPRA changes.

If OPRA does not contain a usable parametric EQ for the headphone, ChatGPT should tell you instead of inventing one.

---

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

## 2. Inventory the complete profile set

Before writing config, list all usable `parametric_eq` entries for the logical product and note:

- exact OPRA EQ ID;
- author;
- details/measurement text;
- whether the profile identifies a variant such as Gold/Silver, pad condition, nozzle, revision, or other tuning distinction;
- whether an apparently duplicated profile is actually identical to one in another formatting-only alias.

The default goal is complete coverage. Every usable parametric profile must either be routed to a target or be an exact semantic duplicate of an imported profile.

## 3. Edit `config/targets.json`

### Simple product: import everything together

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

### Intentional subset only

If the user explicitly asks for only part of a product's profile set, mark that intent:

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
- `output_path`: relative GitHub/Drive folder.
- `include_terms`: optional case-insensitive substring filters against OPRA EQ id, author, and details.
- `include_eq_ids`: optional exact OPRA EQ IDs for precise routing.
- `allow_partial`: optional boolean. Default `false`; when `true`, unmatched profiles for that logical product are allowed because the user intentionally requested a subset.

## 4. Understand the automatic coverage checks

For every configured logical product, the converter:

1. normalizes formatting-only product names (spaces/punctuation/case) to discover possible aliases;
2. gathers every parametric EQ across those aliases;
3. checks which EQs are routed by the config;
4. treats an unmatched alias EQ as covered only when its author/details/filter parameters are semantically identical to an imported EQ;
5. fails if any non-duplicate EQ is left unmatched, unless the logical product is explicitly partial;
6. fails if one EQ is routed to multiple different output folders.

This safeguard is what prevents the original `HD650` / `HD 650` type of omission from happening silently again.

## 5. Save the config and check the build

When `config/targets.json` changes on `main`, the `Update OPRA presets` GitHub Action runs automatically after Actions has been enabled for that repository/fork.

It will:

1. regenerate documentation;
2. run converter tests;
3. download the current OPRA database;
4. validate target matching, logical-product coverage, duplicate aliases, and overlapping routes;
5. generate the XML library;
6. update `output/manifest.json` and XML files only when actual output changed.

A red coverage failure is a request for classification, not permission to weaken the validation.

## 6. Inspect `output/manifest.json`

The manifest shows per-preset metadata plus a top-level `coverage` section.

For each logical product, check:

- `mode`: `complete` or `partial`;
- `opra_parametric_profiles`;
- `matched_profiles`;
- `duplicate_profiles_covered`;
- `unmatched_profiles`.

For a normal complete addition, `unmatched_profiles` must be empty.

## 7. Google Drive sync

GitHub does not receive your Google credentials and does not directly write to Drive.

When ChatGPT has Google Drive write actions connected, it mirrors generated files under:

`Google Drive / OPRA UAPP Presets /`

A model root can contain XML files directly while also containing managed variant subfolders. For example:

```text
OPRA UAPP Presets/
└── SIMGOT/
    └── EW300/
        ├── AutoEQ - Measured by Kazi.xml
        ├── Gold/
        ├── Silver/
        └── DSP/
```

The sync adds/updates generated XML files, removes obsolete generated XML files only within managed locations, preserves unrelated Drive content, and updates the root `manifest.json`.

## Removing a headphone

Delete the applicable target object(s) from `config/targets.json` and save the change.

If multiple entries represent aliases or variants of one model, remove the whole intended logical set unless you specifically want to keep a subset. Rebuild first, then mirror the resulting managed changes to Drive.

## Important rules

- Never invent OPRA product names, IDs, variants, or EQ profiles.
- Always inventory formatting-only OPRA aliases before selecting targets.
- Complete coverage is the default.
- Ask the user when classification is genuinely ambiguous; do not guess a folder.
- Use exact `include_eq_ids` for one-off routing when that is safer than a broad text filter.
- Use `allow_partial` only when the user explicitly requests a subset.
- Never weaken coverage validation merely to make a build green.
- Never manually edit generated XML files as the normal workflow.
- Preserve OPRA and individual EQ creator attribution.
- Do not silently drop unsupported filter types.
- UAPP/ToneBoosters is limited to 10 bands in this converter. If OPRA provides more, OPRA's priority order is used and the manifest records a warning.
- Never commit Google OAuth tokens, service-account keys, GitHub personal access tokens, or other credentials to this repository.
