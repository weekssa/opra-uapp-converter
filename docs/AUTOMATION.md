# Automation architecture

This project has two automation layers.

## 1. OPRA → GitHub output

GitHub Actions runs `.github/workflows/update-presets.yml` once per day and on relevant source/config changes.

The workflow:

1. Runs the converter tests.
2. Downloads OPRA's supported `database_v1.jsonl` feed.
3. Generates the configured UAPP/ToneBoosters XML presets under `output/`.
4. Uploads the generated output as a short-lived workflow artifact for debugging/recovery.
5. Commits the output only if the actual preset library changed.

The generated output is deterministic, so unchanged OPRA data does not create a daily noise commit.

`config/targets.json` defines which products/variants are managed.

## 2. GitHub output → Google Drive

A recurring ChatGPT scheduled task uses the connected GitHub and Google Drive accounts to mirror the repository's current generated output into:

`OPRA UAPP Presets`

The sync is **config-driven**.

It reads:

- `config/targets.json`
- `output/manifest.json`

Every `output_path` in `config/targets.json` becomes a managed relative path underneath the Drive root.

Example:

```json
{
  "vendor_id": "hifiman",
  "product_name": "Edition XS",
  "output_path": "HIFIMAN/Edition XS"
}
```

maps to:

`Google Drive / OPRA UAPP Presets / HIFIMAN / Edition XS`

When a new target is added, the Drive sync can create missing destination folders automatically. No separate hard-coded folder list needs to be maintained.

The Drive sync:

1. Confirms the latest GitHub `Update OPRA presets` workflow succeeded.
2. Reads the current target config and manifest.
3. Creates missing managed Drive folders when needed.
4. Adds new XML files.
5. Replaces changed XML files.
6. Removes obsolete XML files only within configured managed folders.
7. Updates the root `manifest.json`.
8. Does not modify unrelated Drive content.
9. Stays silent when GitHub and Drive are already in sync.

`output/manifest.json` is the source of truth for which generated preset files should exist.

## What happens when you add a headphone

For a normal addition, only `config/targets.json` changes.

That config change triggers GitHub Actions immediately. Once the output is rebuilt successfully, the recurring Drive sync discovers the new `output_path` from the config and mirrors the new XML files into Drive.

See:

- `docs/ADDING_HEADPHONES.md` for manual instructions.
- `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` for the AI-assisted workflow.

## Failure behavior

The system is intentionally conservative.

A GitHub build fails rather than silently producing incorrect output when, for example:

- a configured target matches no OPRA parametric EQ entries;
- an OPRA target contains a filter type the converter cannot map safely;
- a value falls outside the supported ToneBoosters conversion range.

The Drive sync should not mirror a failed/partial build. It first confirms that the latest GitHub workflow completed successfully.
