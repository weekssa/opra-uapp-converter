# Adding headphones

This project is designed so normal headphone additions require editing only one file:

`config/targets.json`

You do **not** need to change the converter code for a normal OPRA headphone addition.

## Easiest method: ask the ChatGPT Project

In the ChatGPT Project for this repository, use a request like:

> Add the FiiO FT1 to my OPRA UAPP converter. Find the exact current OPRA vendor/product information, update `config/targets.json`, verify the GitHub Action succeeds, and confirm which UAPP XML presets were generated. Do not change converter code unless the current config format cannot represent the headphone.

ChatGPT should:

1. Inspect OPRA for the exact product.
2. Confirm that OPRA actually has parametric EQ data for it.
3. Read the current `config/targets.json` first.
4. Add the smallest necessary config entry or entries.
5. Let GitHub Actions rebuild the preset library.
6. Verify the workflow succeeded and inspect `output/manifest.json`.
7. Let the scheduled Drive sync create/mirror the new folder automatically.

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

Example for the existing Edition XS target:

- Vendor folder: `hifiman`
- Product name: `Edition XS`

## 2. Edit `config/targets.json`

Open `config/targets.json` in this repository and add an object inside the `targets` array.

Basic example:

```json
{
  "vendor_id": "hifiman",
  "product_name": "Edition XS",
  "output_path": "HIFIMAN/Edition XS"
}
```

### What each field means

- `vendor_id`: exact OPRA vendor folder/id.
- `product_name`: exact OPRA product name.
- `output_path`: folder to create under both GitHub `output/` and Google Drive `OPRA UAPP Presets/`.
- `include_terms`: optional list used when one OPRA product contains identifiable variants and you want separate folders.

If `include_terms` is omitted, every parametric EQ profile for that product is included.

## 3. Variant example

The SIMGOT EW300 uses one OPRA product with Gold and Silver measurement variants, so it has two target entries:

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

`include_terms` is matched against the OPRA EQ id, author, and details text. A preset is included when any configured term is present.

Use variant filtering only when it is actually needed. For most headphones, omit `include_terms`.

## 4. Save the config change

When `config/targets.json` changes on the `main` branch, the `Update OPRA presets` GitHub Action runs automatically.

It will:

1. Run the converter tests.
2. Download the current OPRA database.
3. Generate the target XML presets.
4. Fail if the target matches no OPRA EQ profiles.
5. Fail if a required filter type cannot be converted safely.
6. Update `output/manifest.json` and XML files only when the actual output changed.

## 5. Check the result

Open:

`Actions → Update OPRA presets`

The latest run should be green.

Then inspect:

`output/manifest.json`

Search for your headphone. The manifest shows:

- XML filename
- OPRA EQ id
- manufacturer/product
- author
- tuning/measurement details
- source link when available
- preamp
- source band count
- UAPP band count
- conversion warnings

## 6. Google Drive happens automatically

You do not need to create the Drive folder manually.

The scheduled ChatGPT Drive sync reads `config/targets.json` and `output/manifest.json`. Every configured `output_path` is treated as a managed folder underneath:

`Google Drive / OPRA UAPP Presets /`

For example:

`"output_path": "FiiO/FT1"`

becomes:

`Google Drive / OPRA UAPP Presets / FiiO / FT1 /`

The sync creates missing folders, adds/updates the generated XML files, and removes obsolete XML files only from folders managed by this project.

## Removing a headphone

Delete its target object from `config/targets.json` and save the change.

GitHub Actions will regenerate the output without that target. The Drive sync will mirror the currently configured managed folders. If you intentionally want an old Drive folder removed entirely, ask the ChatGPT Project to clean it up so unrelated Drive content is not accidentally deleted.

## Important rules

- Never invent OPRA product names or vendor ids.
- Never manually edit generated XML files as the normal workflow.
- Generated files under `output/` should come from the converter.
- Preserve OPRA and individual EQ creator attribution.
- If a build fails after adding a headphone, inspect the error before changing converter behavior.
- Do not silently drop unsupported filter types.
- UAPP/ToneBoosters is limited to 10 bands in this converter. If OPRA provides more, OPRA's priority order is used and the manifest records a warning.
