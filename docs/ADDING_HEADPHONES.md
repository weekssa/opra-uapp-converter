# Adding headphones

This project is designed so normal headphone additions require editing only one file:

`config/targets.json`

You do **not** need to change the converter code for a normal OPRA headphone addition.

If you are using your own public fork, complete [`NEW_USER_SETUP.md`](NEW_USER_SETUP.md) first so GitHub Actions is enabled for your fork and ChatGPT is connected to your own GitHub repository and Google Drive.

## Easiest method: ask the ChatGPT Project

In the ChatGPT Project for this repository, use a request like:

> Add the FiiO FT1 to my OPRA UAPP converter. Find the exact current OPRA vendor/product information, update `config/targets.json`, verify the GitHub Action succeeds, and confirm which UAPP XML presets were generated. Do not change converter code unless the current config format cannot represent the headphone.

ChatGPT should:

1. Inspect OPRA for the exact product.
2. Check the same vendor for near-duplicate product records whose names differ only by spaces, punctuation, hyphens, capitalization, or similar formatting, and compare their available parametric EQ profiles before choosing one.
3. Confirm that OPRA actually has parametric EQ data for the selected record.
4. Read the current `config/targets.json` first.
5. Add the smallest necessary config entry or entries.
6. Let GitHub Actions rebuild the preset library.
7. Verify the workflow succeeded and inspect `output/manifest.json`.
8. Confirm the generated preset count matches the usable parametric EQ profiles expected from the selected OPRA record (or the expected filtered subset when variants are intentionally filtered).
9. If Google Drive write actions are connected, immediately create/mirror the new Drive folder/files and update the Drive root `manifest.json`.
10. Leave the recurring Drive sync as a safety net for later OPRA changes.

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

### Important: check for near-duplicate OPRA product records

Do not stop after finding the first similar-looking product name. OPRA can contain separate records whose names differ only by formatting such as spaces or punctuation.

For example, OPRA currently contains both `HD650` and `HD 650` under Sennheiser, and they do not expose the same EQ profile set. Before choosing a `product_name`, inspect every near-identical candidate's `eq/` directory and compare the available parametric EQ profiles.

If you cannot tell which candidate represents the requested headphone, do not guess.

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

When `config/targets.json` changes on the `main` branch, the `Update OPRA presets` GitHub Action runs automatically **after Actions has been enabled for that repository/fork**.

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

Before considering the addition complete, compare the number of generated files for that target with the number of usable parametric EQ profiles you found in the selected OPRA product. If the counts do not match, investigate the discrepancy before syncing Drive.

## 6. Google Drive sync

GitHub does not receive your Google credentials and does not directly write to Drive.

When ChatGPT has Google Drive write actions connected, it can mirror the generated files into your private Drive root:

`Google Drive / OPRA UAPP Presets /`

For example:

`"output_path": "FiiO/FT1"`

becomes:

`Google Drive / OPRA UAPP Presets / FiiO / FT1 /`

The sync creates missing folders, adds/updates the generated XML files, removes obsolete XML files only from folders managed by this project, and updates the root `manifest.json`.

Your Drive folder does not need to be public or shared with GitHub.

## Removing a headphone

Delete its target object from `config/targets.json` and save the change.

GitHub Actions will regenerate the output without that target. The Drive sync will mirror the currently configured managed folders. If you intentionally want an old Drive folder removed entirely, ask the ChatGPT Project to clean it up so unrelated Drive content is not accidentally deleted.

## Important rules

- Never invent OPRA product names or vendor ids.
- Always check for near-duplicate OPRA product records before selecting a target.
- Verify the expected OPRA parametric profile count against the generated manifest before declaring an addition successful.
- Never manually edit generated XML files as the normal workflow.
- Generated files under `output/` should come from the converter.
- Preserve OPRA and individual EQ creator attribution.
- If a build fails after adding a headphone, inspect the error before changing converter behavior.
- Do not silently drop unsupported filter types.
- UAPP/ToneBoosters is limited to 10 bands in this converter. If OPRA provides more, OPRA's priority order is used and the manifest records a warning.
- Never commit Google OAuth tokens, service-account keys, GitHub personal access tokens, or other credentials to this repository.
