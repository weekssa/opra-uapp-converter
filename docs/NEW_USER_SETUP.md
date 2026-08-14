# New user setup: your own fork + private Google Drive

This guide is for someone who wants an independent OPRA → UAPP/ToneBoosters preset library, using their own GitHub repository and their own private Google Drive.

GitHub and Google Drive are separate account connections. Never put Google passwords, OAuth tokens, service-account keys, ChatGPT credentials, Drive folder IDs, or GitHub personal access tokens in this repository.

## 1. Fork the repository

After the upstream repository is public:

1. Open `https://github.com/weekssa/opra-uapp-converter`.
2. Click **Fork**.
3. Choose your GitHub account.
4. Keep the name `opra-uapp-converter` unless you need another name.
5. Create the fork.

Your repository will normally be:

`YOUR_GITHUB_USERNAME/opra-uapp-converter`

A normal fork of a public repository is public. If you require a private repository, create a separate private repository instead.

## 2. Enable GitHub Actions

In your fork:

1. Open **Actions**.
2. Enable workflows if GitHub asks.
3. Open **Update OPRA presets**.
4. Enable that workflow if needed.
5. Run it once from `main`.
6. Confirm the run finishes green.

The workflow needs repository `contents: write` so it can commit generated output/docs. Do not add a personal access token unless your environment has a separate reason to require one.

## 3. Connect GitHub to ChatGPT

In ChatGPT, connect the GitHub app and authorize your fork.

The Project must be able to read the repository because the small Project Instructions bootstrap deliberately loads the detailed maintenance runbook from GitHub. If repository write actions are available, authorize them so ChatGPT can edit config/docs directly. If only read access is available, ChatGPT can still inspect/plan correctly and should give the smallest manual edit required.

## 4. Connect your Google Drive

Connect Google Drive to ChatGPT using the Google account that will own the preset library.

For automatic mirroring, the connection needs Drive actions that can create folders and create/update/upload files. Read-only Drive access is not enough for automatic synchronization.

GitHub never receives your Google credentials.

## 5. Create the private Drive root

Create:

`OPRA UAPP Presets`

It may remain private.

Managed paths are created underneath it, for example:

`OPRA UAPP Presets / Sennheiser / HD650`

A model root may contain XMLs directly and also contain variant child folders.

## 6. Create the ChatGPT Project

Create a new ChatGPT Project and open **Project settings → Project instructions**.

Paste the contents of:

`docs/CHATGPT_PROJECT_INSTRUCTIONS.md`

That file is intentionally a **short paste-ready bootstrap** and is kept below the ChatGPT Project instruction-length limit.

Before pasting, replace:

`YOUR_GITHUB_USERNAME/opra-uapp-converter`

with the exact repository for your installation.

Keep the Drive root:

`OPRA UAPP Presets`

### Why the instructions are split

Do **not** paste `docs/CHATGPT_MAINTENANCE_RUNBOOK.md` into Project Instructions.

The detailed runbook is intentionally kept in GitHub because Project Instructions have a limited text field. The bootstrap tells ChatGPT to read the current runbook from the connected repository before OPRA maintenance work.

This gives the Project two layers:

1. `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` — small, stable bootstrap that fits Project settings and contains the most important safety gates.
2. `docs/CHATGPT_MAINTENANCE_RUNBOOK.md` — detailed GitHub-hosted behavior that can grow and be updated without overflowing the Project settings field.

When the repository's maintenance behavior changes, update the runbook and bootstrap as appropriate. A new Project only needs the paste-ready bootstrap plus access to the repository.

## 7. Test repository access

Ask:

`What headphones do I have configured?`

ChatGPT should read your fork's `config/targets.json`.

If it cannot access the repository, fix the GitHub app authorization before testing additions.

## 8. Test the new-headphone approval flow

Try a request such as:

`Add the Sony WF-1000XM5`

Expected behavior **before any config change**:

1. ChatGPT reads the current GitHub maintenance runbook/config/docs/manifest.
2. It identifies the exact OPRA product and subtype.
3. It mentions meaningful near-name products when relevant (for Sony, WF vs WH can matter).
4. GitHub search may locate the product, but is treated as discovery-only.
5. ChatGPT directly enumerates:
   `database/vendors/<vendor_id>/products/<product_folder>/eq/`
6. It opens every child EQ `info.json`.
7. It includes formatting-only aliases when appropriate.
8. It cross-checks the exact usable parametric-EQ IDs/count with:
   `https://opra.roonlabs.net/database_v1.jsonl`
9. If repository/feed disagree, it stops and explains the discrepancy.
10. If they agree, it shows a verification summary and the complete numbered candidate list.
11. It waits for you to choose **Import all**, **Import only selected EQs**, or **Import all except selected EQs**.

A correct Project must **not** edit `config/targets.json` merely because you said `Add [headphone]`.

The candidate list should show each proposed UAPP name, creator/details, exact OPRA EQ ID, band count, proposed folder/variant, and source link when OPRA provides one.

You can reply naturally, for example:

```text
All
Only 1, 3, and 4
All except 2
Everything except the Rtings profile
```

Only after that approval should ChatGPT edit config/build/sync.

## 9. Understand selection behavior

### Import all

Use normal complete routing. Future OPRA profiles that unambiguously fit the route can be included normally.

### Import only selected EQs

The project normally records exact `include_eq_ids` with intentional partial mode. The selected set stays fixed until you change it; later OPRA profiles do not silently join it.

### Import all except selected EQs

The project records exact `exclude_eq_ids`. Only those exact profiles remain excluded; future unrelated matching profiles can still be imported.

Exact include/exclude IDs are validated. Typos/stale IDs must fail rather than silently changing your preference.

## 10. UAPP-visible naming

UAPP may show only the embedded preset name rather than its source folder. Generated presets therefore use:

`Model [Variant] - Creator - Details`

Examples:

```text
EW300 Gold - AutoEQ - Fahryst
EW300 DSP - AutoEQ - Jaytiss
Edition XS - AutoEQ - Rtings
HD650 - oratory1990 - Harman Target
```

The XML filename, embedded ToneBoosters preset Name, and manifest `preset_name` are kept consistent. Original OPRA author/details/source metadata remains separately preserved in `output/manifest.json`.

Do not rename generated XMLs manually.

## 11. What ChatGPT does after approval

For a normal addition it should:

1. represent exactly the approved selection in `config/targets.json`;
2. choose clean `Manufacturer/Model` or `Manufacturer/Model/Variant` output paths;
3. run/verify **Update OPRA presets**;
4. confirm `src/update_docs.py` regenerated supported-headphone/project-description documentation;
5. validate `output/manifest.json` coverage, exclusions, names, attribution, sources, warnings, and errors;
6. fix real validation failures rather than weakening safeguards;
7. if Drive write actions exist, immediately mirror generated XMLs and root `manifest.json` into your private Drive.

See `docs/ADDING_HEADPHONES.md` for detailed routing/config behavior.

## 12. Completeness safeguards

For a normally managed logical product, every usable OPRA parametric EQ must be:
- imported;
- duplicate-covered;
- explicitly excluded by exact ID;
- or intentionally outside a fixed user-selected subset.

The build also checks formatting-only product aliases and rejects overlapping routing.

`allow_partial: true` is only for intentional subsets, never a generic way to hide missing profiles.

If a later OPRA change breaks coverage, ChatGPT should inspect the exact product directory/feed and new profile rather than guessing.

## 13. Test Drive access

Ask:

`Is Drive up to date?`

ChatGPT should compare the current GitHub manifest/output with **your** `OPRA UAPP Presets` folder.

When writes are available it may fix managed differences, including safe generated-file renames/removals, without modifying unrelated Drive content.

## 14. Optional recurring Drive sync

The GitHub Action refreshes generated output. Drive mirroring is separate because this repository stores no Google credentials.

A recurring ChatGPT task can:
- confirm the latest GitHub build succeeded;
- read config/manifest;
- validate coverage/naming/selection state;
- compare managed GitHub output with Drive;
- mirror additions/changes/renames/removals;
- update Drive `manifest.json`;
- stay silent when everything is current.

Interactive headphone additions should still sync immediately after approval + successful build when Drive write actions are available. The recurring task is only the safety net.

## Important repository documentation

- `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` — paste-ready Project bootstrap; must remain below the UI limit.
- `docs/CHATGPT_MAINTENANCE_RUNBOOK.md` — full GitHub-hosted ChatGPT behavior.
- `docs/ADDING_HEADPHONES.md` — routing/config details.
- `docs/AUTOMATION.md` — automation/Drive architecture.
- `config/targets.json` — configured managed targets.
- `output/manifest.json` — generated preset/coverage source of truth.
- `docs/PROJECT_DESCRIPTION.md` — generated repository/project description.

## Privacy summary

- Your repository contains converter code/config/generated OPRA-derived output and attribution.
- Your Google Drive remains governed by your Google sharing settings.
- A public fork does not make your Drive public.
- Never commit credentials or private Drive links/IDs.
- Each user connects ChatGPT separately to their GitHub repository and Google Drive.
