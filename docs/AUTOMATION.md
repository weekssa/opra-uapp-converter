# Automation architecture

This project has two intentionally separate automation layers, plus one required interactive approval checkpoint when a new headphone is added through ChatGPT.

## New-headphone approval checkpoint

A new-headphone request is intentionally a **two-stage workflow**:

1. **Inventory verification and user approval** — ChatGPT identifies the exact OPRA product, directly enumerates its real `eq/` directory, checks formatting-only aliases, cross-checks the usable parametric-EQ IDs against `database_v1.jsonl`, proposes routing/UAPP-visible names, then shows the verified complete candidate list and waits for the user's preference.
2. **Configuration/build/sync** — only after approval does ChatGPT update `config/targets.json`, validate the GitHub build, inspect the manifest, and mirror the approved output to Drive.

The user can choose:

- **Import all**
- **Import only selected EQs**
- **Import all except selected EQs**

The initial `Add [headphone]` request is not itself permission to silently import every profile.

The candidate list should include a numbered entry for every verified usable OPRA parametric EQ with its proposed UAPP-visible name, creator/details, exact OPRA EQ ID, band count, proposed folder/variant, and source link when available.

This human approval checkpoint and the converter's technical coverage checks solve different problems: the checkpoint confirms the user's preference, while the converter verifies that the approved preference was represented accurately and no unrelated profile disappeared accidentally.

## Pre-import OPRA inventory verification guard

The approval list itself must be verified before it is shown to the user.

### GitHub search is discovery-only

GitHub search can be used to locate a likely product record, but search results are not an authoritative directory listing. They may omit valid files. Search result count must never be used as the EQ count.

After the exact product record is identified, ChatGPT must directly enumerate:

`database/vendors/<vendor_id>/products/<product_folder>/eq/`

Every child EQ folder must be opened and its `info.json` inspected. Only entries whose OPRA `type` is `parametric_eq` are usable candidates for this converter.

The same direct enumeration must be performed for formatting-only aliases that are being treated as part of the same logical product.

### Supported-feed cross-check

The converter consumes OPRA's supported distribution feed:

`https://opra.roonlabs.net/database_v1.jsonl`

Before user approval, the exact parametric-EQ ID set obtained from the primary OPRA repository must be compared with the exact IDs present for the same product record(s) in `database_v1.jsonl`.

The pre-import gate passes only when the repository and feed agree on the usable parametric-EQ set. If they disagree, ChatGPT must stop before editing config or presenting a supposedly complete approval list and explain the discrepancy.

This guard is intentionally separate from the converter's post-config coverage validation. Coverage validation can prove that configured feed entries were accounted for; it cannot repair an approval list that was incomplete because discovery relied on partial code-search results.

### Similar-product disambiguation

Before the EQ list, ChatGPT should state the exact matched OPRA product name, product folder, and subtype. When the same vendor contains an obviously similar sibling name, mention it rather than silently switching products.

Example:

```text
Matched: Sony WF-1000XM5 (in-ear)
Similar OPRA product: Sony WH-1000XM5 (over-ear)
Proceeding with WF-1000XM5 because that is the requested model.
```

The approval message should also state the verification totals, for example:

```text
OPRA directory: 8 EQ folders
Usable parametric EQs: 8
Supported database_v1.jsonl feed: the same 8 EQ IDs
```

## 1. OPRA → GitHub output

GitHub Actions runs `.github/workflows/update-presets.yml` once per day and on relevant source/config changes.

The workflow:

1. Regenerates documentation from `config/targets.json`.
2. Runs the converter and documentation-safeguard tests.
3. Downloads OPRA's supported `database_v1.jsonl` feed.
4. Validates target matching, exact include/exclude IDs, formatting-only product aliases, profile coverage, route exclusivity, and UAPP-visible preset naming.
5. Generates the configured UAPP/ToneBoosters XML presets under `output/`.
6. Uploads the generated output as a short-lived workflow artifact for debugging/recovery.
7. Commits output/documentation only if the actual repository content changed.

The generated output is deterministic, so unchanged OPRA data does not create a daily noise commit.

`config/targets.json` defines which products/variants are managed, which exact profiles are selected/excluded when applicable, and how each OPRA profile is routed.

## Selection/exclusion guard

The configuration supports three user-approved import styles.

### Import all

A normal target without selection filters imports every parametric EQ for that exact OPRA product record, subject to variant routing when multiple targets are required.

### Import only selected EQs

Use exact `include_eq_ids` plus `allow_partial: true` where practical. This creates a fixed approved subset: profiles outside the list remain non-imported until the user changes the selection.

### Import all except selected EQs

Use exact `exclude_eq_ids`. The excluded IDs are accounted for separately without disabling normal unmatched-profile detection.

The converter validates every configured `include_eq_ids` and `exclude_eq_ids` entry against the current OPRA parametric EQ IDs for that exact target product. A stale or mistyped exact ID fails the build. The same EQ ID cannot be both included and excluded in one target.

`output/manifest.json` reports exact user exclusions in `coverage[].explicitly_excluded_profiles`.

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

The GitHub build is intentionally responsible for detecting profiles that would otherwise be missed silently after configuration.

For each configured logical product, the converter normalizes formatting-only differences in product names (spaces, punctuation, capitalization) and audits every OPRA `parametric_eq` profile across those possible aliases in the supported feed.

A normal product is in **complete** mode. Every OPRA parametric profile must be one of:

- matched/imported;
- a verified semantic duplicate of an imported profile;
- explicitly excluded by exact EQ ID after user approval.

An unmatched profile is accepted as duplicate-covered only when its author, details, type, preamp/filter parameters are semantically identical to an imported profile. Source-link differences are ignored for duplicate detection so the configuration can deliberately keep the richer-attributed copy.

The build fails when a non-duplicate, non-excluded profile is not matched by any target in complete mode.

The build also fails if a single OPRA profile matches multiple different `output_path` values. This prevents a broad root rule and a variant rule from silently duplicating the same preset into multiple folders.

If a user explicitly requests only a fixed subset of a logical product, a target can set:

```json
"allow_partial": true
```

That changes the coverage report to `partial` and allows non-selected OPRA profiles. This setting must reflect a deliberate user choice; it is not a generic workaround for a failed build.

`output/manifest.json` records coverage status for each logical product:

- complete/partial mode;
- total OPRA parametric profile count across aliases;
- matched profile count;
- duplicate-covered profile count;
- explicitly excluded profile IDs;
- unmatched profile IDs.

### New OPRA profile behavior

When OPRA adds a new profile to a configured complete product:

- if an existing rule clearly matches it and it is not explicitly excluded, it is generated normally with the standard headphone-first name;
- if no rule matches it, the GitHub build fails;
- if it would match multiple variant folders, the GitHub build fails.

An `exclude_eq_ids` entry applies only to the exact ID the user excluded; it does not suppress future unrelated profiles.

A fixed `include_eq_ids` + `allow_partial` selection behaves differently by design: newly added profiles stay outside that approved subset until the user changes it.

The maintenance workflow must inspect any new coverage/routing failure. If its intended folder is obvious from OPRA metadata, update config accordingly. If classification is ambiguous, ask the user what they want before changing folders or weakening validation.

This means ambiguity becomes a visible maintenance event instead of silent data loss or silent misclassification.

## Exact one-off routing

`include_eq_ids` can also route a known OPRA EQ ID exactly. It is preferable to a broad substring rule when one unclassified profile belongs directly in a model root while sibling profiles are split into variants.

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

<!-- VERSIONING_START -->
## Automatic project versioning

The tracked [`VERSION`](../VERSION) file currently contains **1.0.0** and follows Semantic Versioning (`MAJOR.MINOR.PATCH`).

The `Update OPRA presets` workflow decides the bump only after a successful preset generation:

- **Minor** — `config/targets.json` changed in the triggering push. This represents a change to the managed headphone/variant set or its approved routing/selection configuration.
- **Patch** — the generated `output/` changed while the configured target file did not. This covers upstream OPRA changes that alter the managed preset library and converter changes that materially alter generated output.
- **Major** — intentionally changed by a maintainer for a breaking converter or preset-format change. Major versions are never guessed automatically.
- **No bump** — no configured-target change and no generated-output change. Daily scheduled checks therefore do not create version noise.

After deciding the version, the workflow regenerates the README and `docs/PROJECT_DESCRIPTION.md`, runs the test suite, and commits `VERSION`, generated output, and generated documentation together when anything changed.

This design deliberately uses the normal short-lived GitHub Actions `GITHUB_TOKEN` with `contents: write`. It does **not** store an Administration-level personal access token merely to keep GitHub's cosmetic About/Description field synchronized. The repository About text may remain a stable summary while the README and generated project description carry the current version and complete configured-headphone information.
<!-- VERSIONING_END -->

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
3. Verifies the manifest has no errors or unexpected unmatched profiles for complete products.
4. Treats `explicitly_excluded_profiles` as valid only when they correspond to exact configured user exclusions.
5. Verifies generated `preset_name` values use the expected headphone/model prefix.
6. Creates missing managed Drive folders when needed.
7. Adds new XML files.
8. Replaces changed or renamed XML files.
9. Removes obsolete generated XML files only within the applicable managed folder level.
10. Updates the root `manifest.json`.
11. Does not modify unrelated Drive content.
12. Stays silent when GitHub and Drive are already in sync.

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

For a normal addition, only `config/targets.json` should need to change **after user approval**.

Before that change is made, the maintenance workflow verifies the product inventory by direct OPRA directory enumeration plus `database_v1.jsonl` cross-check, checks formatting-only aliases, proposes the UAPP names/folders, and asks the user to approve all/some/all-except. The config change then represents that exact decision and triggers GitHub Actions. Once the output is rebuilt successfully with correct coverage/exclusion accounting and headphone-first `preset_name` values, the connected ChatGPT workflow mirrors the resulting XML files and root manifest into that user's Drive.

See:

- `docs/ADDING_HEADPHONES.md` for manual instructions, approval examples, and config fields.
- `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` for the AI-assisted workflow.
- `docs/NEW_USER_SETUP.md` for setting up a fork and private Drive from scratch.

## Failure behavior

The system is intentionally conservative.

A pre-import inventory must stop before approval/config changes when:

- the exact product is not clear;
- a closely named product creates unresolved ambiguity;
- direct OPRA `eq/` enumeration and `database_v1.jsonl` expose different parametric-EQ ID sets/counts.

A GitHub build fails rather than silently producing incorrect/incomplete output when, for example:

- a configured target matches no OPRA parametric EQ entries;
- a configured exact include/exclude EQ ID does not exist for that exact OPRA product;
- the same exact EQ ID is both included and excluded in one target;
- a complete logical product has an unexplained unmatched OPRA parametric profile;
- one OPRA profile matches multiple output folders;
- an OPRA target contains a filter type the converter cannot map safely;
- a value falls outside the supported ToneBoosters conversion range.

When a coverage/routing/selection failure requires a choice, the correct response is to inspect OPRA and ask the user if necessary. Do not add `allow_partial`, broaden filters, invent exclusions, or invent a variant just to make the workflow green.

A preset-naming regression is also a release blocker: generated names must keep the headphone/model first so UAPP users can identify the preset without seeing its folder.

The Drive sync must not mirror a failed or unexpectedly incomplete build. It first confirms that the latest GitHub workflow completed successfully and that manifest exclusions/partial mode match intentional config.

## Credential safety

Never commit any of the following to the repository:

- Google OAuth tokens;
- Google service-account JSON files;
- GitHub personal access tokens;
- ChatGPT credentials;
- `.env` files containing secrets;
- private keys.

The repository `.gitignore` excludes common local credential filenames as an additional guardrail, but users remain responsible for keeping secrets out of Git history.