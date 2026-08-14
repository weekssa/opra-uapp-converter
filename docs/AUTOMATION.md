# Automation architecture

This project has two automation layers.

## 1. OPRA → GitHub output

GitHub Actions runs `.github/workflows/update-presets.yml` once per day and on relevant source/config changes.

The workflow:

1. Runs the converter tests.
2. Downloads OPRA's supported `database_v1.jsonl` feed.
3. Generates the configured UAPP/ToneBoosters XML presets under `output/`.
4. Commits the output only if the actual preset library changed.

The generated output is deterministic, so an unchanged OPRA dataset does not create a daily noise commit.

## 2. GitHub output → Google Drive

A ChatGPT scheduled task uses the connected GitHub and Google Drive accounts to mirror the repository's current `output/` into the existing Drive folder:

`OPRA UAPP Presets`

Managed Drive folders:

- `HIFIMAN/Edition XS`
- `SIMGOT/EW300/Gold`
- `SIMGOT/EW300/Silver`
- `SIMGOT/EW300/DSP`

The Drive sync runs after the GitHub refresh, compares the current manifest/output, replaces changed files, adds new files, removes obsolete XML files only from those managed folders, and remains silent when nothing changed.

`output/manifest.json` is the source of truth for the preset files that should exist in Drive.

## Adding headphones later

Add another entry to `config/targets.json`. The converter and GitHub workflow do not need to be rewritten for normal product additions. If a new OPRA preset uses a ToneBoosters filter type that this converter does not support, the build intentionally fails rather than silently generating an incorrect EQ.

After adding a new Drive destination to the target config, the Drive sync task should also be updated to include that managed destination.
