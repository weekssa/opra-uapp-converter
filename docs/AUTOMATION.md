# Automation architecture

This project has two intentionally separate automation layers.

## 1. OPRA → GitHub output

GitHub Actions runs `.github/workflows/update-presets.yml` once per day and on relevant source/config changes.

The workflow:

1. Regenerates documentation from `config/targets.json`.
2. Runs the converter tests.
3. Downloads OPRA's supported `database_v1.jsonl` feed.
4. Validates target matching, formatting-only product aliases, profile coverage, route exclusivity, and UAPP-visible preset naming.
5. Generates the configured UAPP/ToneBoosters XML presets under `output/`.
6. Uploads the generated output as a short-lived workflow artifact for debugging/recovery.
7. Commits output/documentation only if the actual repository content changed.

The generated output is deterministic, so unchanged OPRA data does not create a daily noise commit.

`config/targets.json` defines which products/variants are managed and how each OPRA profile is routed.

## UAPP-visible preset naming guard

UAPP's preset picker does not show the source folder. Every generated preset therefore uses the deterministic format:

```text
Model [Variant] - Creator - Details
```

The model/variant prefix is derived from `output_path` by dropping the first manufacturer component and joining the remaining components with spaces. Examples:

```text
HIFIMAN/Edition XS     -> Edition XS
SIMGOT/EW300           -> EW300
SIMGOT/EW300/Gold      -> EW300 Gold
SIMGOT/EW300/DSP       -> EW300 DSP
Sennheiser/HD650       -> HD650
```

The converter writes this generated name both as the XML filename and the embedded ToneBoosters `PresetInfo Name`, and records it in `output/manifest.json` as `preset_name`.

Display-only compaction removes a leading `Measured by ` from OPRA details and removes a trailing parenthetical variant only when it duplicates the configured variant. Original OPRA `author` and `details` are preserved unchanged in the manifest.

Unit tests assert representative names such as:

```text
EW300 Gold - AutoEQ - Fahryst
EW300 - AutoEQ - Kazi
HD650 - oratory1990 - Harman Target
```

This naming behavior is global converter behavior. New headphones inherit it automatically; maintenance should not add per-headphone filename hacks.

## Completeness guard

The GitHub build is intentionally responsible for detecting profiles that would otherwise be missed silently.

For each configured logical product, the converter normalizes formatting-only differences in product names (spaces, punctuation, capitalization) and audits every OPRA `parametric_eq` profile across those possible aliases.

A normal product is in **complete** mode. The build fails if a non-duplicate profile is not matched by any target.

An unmatched profile is accepted as duplicate-covered only when its author, details, type, preamp/filter parameters are semantically identical to an imported profile. Source-link differences are ignored for duplicate detection so the configuration can deliberately keep the richer-attributed copy.

The build also fails if a single OPRA profile matches multiple different `output_path` values. This prevents a broad root rule and a variant rule from silently duplicating the same preset into multiple folders.

If a user explicitly requests only a subset of a logical product, a target can set:

```json
"allow_partial": true
```

That changes the coverage report to `partial` and allows unmatched OPRA profiles. This setting must reflect a deliberate user request; it is not a generic workaround for a failed build.

`output/manifest.json` records coverage status for each logical product:

- complete/partial mode;
- total OPRA parametric profile count across aliases;
- matched profile count;
- duplicate-covered profile count;
- unmatched profile IDs.

### New OPRA profile behavior

When OPRA adds a new profile to a configured complete product:

- if an existing rule clearly matches it, it is generated normally with the standard headphone-first name;
- if no rule matches it, the GitHub build fails;
- if it would match multiple variant folders, the GitHub build fails.

The maintenance workflow must inspect that new profile. If its intended folder is obvious from OPRA metadata, update config accordingly. If classification is ambiguous, ask the user what they want before changing folders or weakening validation.

This means ambiguity becomes a visible maintenance event instead of silent data loss or silent misclassification.

## Exact one-off routing

`include_eq_ids` can route a known OPRA EQ ID exactly. It is preferable to a broad substring rule when one unclassified profile belongs directly in a model root while sibling profiles are split into variants.

Current example:

```json
{
  "vendor_id": "simgot_audio",
  "product_name": "EW300",
  "include_eq_ids": ["simgot_audio:ew300::autoeq_kazi"],
  "output_path": "SIMGOT/EW300"
}
```

Gold and Silver are routed separately. If another unclassified EW300 profile appears later, complete-coverage validation stops the build until that new profile is deliberately classified.

### Fork behavior

When this repository is public, another user can fork it and run the same GitHub automation in their own repository.

GitHub disables workflows in a new public fork until the fork owner enables GitHub Actions. Scheduled workflows are also disabled by default on public forks. A fork owner should enable Actions, enable `Update OPRA presets` if necessary, and run it once manually before relying on the daily schedule.

The workflow contains:

```yaml
permissions:
  contents: write
```

That is the repository permission required for the workflow to commit regenerated presets/documentation back to the fork. The project does not require a Google credential, GitHub personal access token, or other external secret in GitHub Actions.

## 2. GitHub output → Google Drive

Google Drive mirroring is deliberately **not** performed by GitHub Actions.

A ChatGPT task uses that user's connected GitHub and Google Drive accounts to mirror the repository's current generated output into a private Drive folder named:

`OPRA UAPP Presets`

This separation is a security feature:

- no Google OAuth token is stored in GitHub;
- no Google service-account key is committed to the repository;
- a public GitHub fork does not grant anyone access to the user's Drive;
- each user authorizes ChatGPT separately to their own GitHub fork and their own Google account.

The Drive sync is **config-driven**.

It reads:

- `config/targets.json`
- `output/manifest.json`

Every `output_path` in `config/targets.json` becomes a managed relative path underneath the connected user's Drive root.

A model root may itself contain generated XML files while also containing variant subfolders. For example:

```text
OPRA UAPP Presets/
└── SIMGOT/
    └── EW300/
        ├── EW300 - AutoEQ - Kazi.xml
        ├── Gold/
        ├── Silver/
        └── DSP/
```

The root target manages generated XML files directly in `EW300`; the variant targets manage their own child folders. Drive synchronization must preserve unrelated content and must not treat a parent managed path as permission to recursively delete unrelated child folders.

When a new target is added, the Drive sync can create missing destination folders automatically. No separate hard-coded folder list needs to be maintained.

When converter naming changes, the Drive sync must treat the manifest's `file` entries as authoritative: renamed generated XML files replace obsolete generated names rather than leaving duplicates behind.

The Drive sync:

1. Confirms the latest GitHub `Update OPRA presets` workflow succeeded.
2. Reads the current target config and manifest.
3. Verifies the manifest has no errors/unexpected unmatched profiles for complete products.
4. Verifies generated `preset_name` values use the expected headphone/model prefix.
5. Creates missing managed Drive folders when needed.
6. Adds new XML files.
7. Replaces changed or renamed XML files.
8. Removes obsolete generated XML files only within the applicable managed folder level.
9. Updates the root `manifest.json`.
10. Does not modify unrelated Drive content.
11. Stays silent when GitHub and Drive are already in sync.

`output/manifest.json` is the source of truth for which generated preset files should exist and what UAPP should display for each preset.

## ChatGPT app permissions

For automated maintenance, the user needs two separate ChatGPT app connections.

### GitHub

The GitHub app must be authorized to access the user's repository/fork. When repository write actions are available in that ChatGPT plan/workspace, they allow ChatGPT to maintain `config/targets.json` and related files directly.

### Google Drive

The Google Drive app must have the Drive actions needed to create folders and upload/update files. A read-only or sync-only connection is not sufficient for automatic mirroring.

The Drive folder itself may remain private. It does not need to be shared with GitHub or the upstream project owner.

See `docs/NEW_USER_SETUP.md` for the user-facing setup steps.

## What happens when you add a headphone

For a normal addition, only `config/targets.json` should need to change.

Before that change is made, the maintenance workflow inventories all OPRA profiles and possible formatting-only aliases. The config change then triggers GitHub Actions. Once the output is rebuilt successfully with complete/intentional-partial coverage and correct headphone-first `preset_name` values, the connected ChatGPT workflow mirrors the resulting XML files and root manifest into that user's Drive.

See:

- `docs/ADDING_HEADPHONES.md` for manual instructions and config fields.
- `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` for the AI-assisted workflow.
- `docs/NEW_USER_SETUP.md` for setting up a fork and private Drive from scratch.

## Failure behavior

The system is intentionally conservative.

A GitHub build fails rather than silently producing incorrect/incomplete output when, for example:

- a configured target matches no OPRA parametric EQ entries;
- a complete logical product has an unmatched OPRA parametric profile;
- one OPRA profile matches multiple output folders;
- an OPRA target contains a filter type the converter cannot map safely;
- a value falls outside the supported ToneBoosters conversion range.

When a coverage/routing failure requires a classification choice, the correct response is to inspect OPRA and ask the user if necessary. Do not add `allow_partial`, broaden filters, or invent a variant just to make the workflow green.

A preset-naming regression is also a release blocker: generated names must keep the headphone/model first so UAPP users can identify the preset without seeing its folder.

The Drive sync must not mirror a failed/partial build that was not intentionally configured. It first confirms that the latest GitHub workflow completed successfully.

## Credential safety

Never commit any of the following to the repository:

- Google OAuth tokens;
- Google service-account JSON files;
- GitHub personal access tokens;
- ChatGPT credentials;
- `.env` files containing secrets;
- private keys.

The repository `.gitignore` excludes common local credential filenames as an additional guardrail, but users remain responsible for keeping secrets out of Git history.
