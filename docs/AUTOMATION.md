# Automation architecture

This project has two intentionally separate automation layers.

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
7. Updates the root `manifest.json` when the sync implementation manages that file.
8. Does not modify unrelated Drive content.
9. Stays silent when GitHub and Drive are already in sync.

`output/manifest.json` is the source of truth for which generated preset files should exist.

## ChatGPT app permissions

For automated maintenance, the user needs two separate ChatGPT app connections:

### GitHub

The GitHub app must be authorized to access the user's repository/fork. When repository write actions are available in that ChatGPT plan/workspace, they allow ChatGPT to maintain `config/targets.json` and related files directly.

### Google Drive

The Google Drive app must have the Drive actions needed to create folders and upload/update files. A read-only or sync-only connection is not sufficient for automatic mirroring.

The Drive folder itself may remain private. It does not need to be shared with GitHub or the upstream project owner.

See `docs/NEW_USER_SETUP.md` for the user-facing setup steps.

## What happens when you add a headphone

For a normal addition, only `config/targets.json` changes.

That config change triggers GitHub Actions immediately. Once the output is rebuilt successfully, the connected ChatGPT workflow discovers the new `output_path` from the config and mirrors the new XML files into that user's Drive.

See:

- `docs/ADDING_HEADPHONES.md` for manual instructions.
- `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` for the AI-assisted workflow.
- `docs/NEW_USER_SETUP.md` for setting up a fork and private Drive from scratch.

## Failure behavior

The system is intentionally conservative.

A GitHub build fails rather than silently producing incorrect output when, for example:

- a configured target matches no OPRA parametric EQ entries;
- an OPRA target contains a filter type the converter cannot map safely;
- a value falls outside the supported ToneBoosters conversion range.

The Drive sync should not mirror a failed/partial build. It first confirms that the latest GitHub workflow completed successfully.

## Credential safety

Never commit any of the following to the repository:

- Google OAuth tokens;
- Google service-account JSON files;
- GitHub personal access tokens;
- ChatGPT credentials;
- `.env` files containing secrets;
- private keys.

The repository `.gitignore` excludes common local credential filenames as an additional guardrail, but users remain responsible for keeping secrets out of Git history.
