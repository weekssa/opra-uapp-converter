# New user setup: your own fork + private Google Drive

This guide is for someone who wants their own independent copy of the OPRA → UAPP converter, their own configured headphones, and their own private Google Drive preset library.

You do **not** share the original owner's Google Drive. Your fork and your Google Drive account stay separate. ChatGPT is authorized to each service through your own account connections.

## What you need

- A GitHub account.
- A ChatGPT plan/workspace where the GitHub and Google Drive apps you need are available.
- A Google account with Google Drive.
- USB Audio Player PRO with the ToneBoosters parametric EQ if you want to use the generated presets in UAPP.

No Google password, OAuth token, service-account key, Drive folder ID, or ChatGPT credential belongs in this GitHub repository.

## 1. Fork the repository

After the upstream repository is public:

1. Open `https://github.com/weekssa/opra-uapp-converter`.
2. Click **Fork**.
3. Choose your GitHub account as the owner.
4. Keep the repository name `opra-uapp-converter` unless you have a reason to change it.
5. Click **Create fork**.

A fork of a public GitHub repository is also public. If you require a private repository, create a separate private repository instead of a normal public fork.

Your repository will normally be:

`YOUR_GITHUB_USERNAME/opra-uapp-converter`

## 2. Enable GitHub Actions in your fork

GitHub does not automatically run workflows in a new public fork, and scheduled workflows are disabled by default on public forks.

1. Open your fork.
2. Click **Actions**.
3. If GitHub shows a warning, click **I understand my workflows, go ahead and enable them**.
4. In the left side of Actions, open **Update OPRA presets**.
5. If the workflow shows as disabled, use its menu and click **Enable workflow**.
6. Click **Run workflow** and run it once from the `main` branch.
7. Confirm the run finishes green.

The workflow already requests only the repository permission it needs to update generated files: `contents: write`.

If an organization policy prevents the workflow from writing back to the fork, the organization/repository administrator must allow the required GitHub Actions token permission. Do not add a personal access token unless you have a separate reason to do so.

GitHub documentation:

- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows

## 3. Connect your fork to ChatGPT

1. In ChatGPT, open **Settings → Apps**.
2. Find **GitHub** and click **Connect**.
3. Complete the GitHub authorization flow.
4. When GitHub asks which repositories ChatGPT can access, include your fork: `YOUR_GITHUB_USERNAME/opra-uapp-converter`.
5. If GitHub is already connected, open the GitHub app in **Settings → Apps** and use **Choose repositories** or **Configure Repositories on GitHub** to add your fork.

GitHub app capabilities can vary by ChatGPT plan/workspace. If repository write actions are available, authorize the fork so ChatGPT can maintain `config/targets.json` and related files for you. If your ChatGPT environment only provides read access, you can still use the GitHub web editor for the config changes described in `docs/ADDING_HEADPHONES.md`.

OpenAI documentation:

- https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt-deep-research
- https://help.openai.com/en/articles/11487775-connectors-in

## 4. Connect your own Google Drive to ChatGPT

1. In ChatGPT, open **Settings → Apps**.
2. Find **Google Drive** and click **Connect**.
3. Choose the Google account where you want your preset library.
4. Approve the Google permissions requested for the Drive actions you intend to use.
5. If you are in a managed Business/Enterprise/Edu workspace, your workspace or Google Workspace administrator may also need to enable/approve the Google Drive actions and OAuth scopes.

For this project to mirror XML files automatically, the Google Drive app must have the Drive **actions** needed to create folders and create/update/upload files. A read-only/sync-only connection is not enough for automatic Drive mirroring.

The Google Drive write actions use Google's Drive scope when enabled. You never copy that OAuth credential into GitHub; ChatGPT keeps the Google connection separate from the repository.

OpenAI documentation:

- https://help.openai.com/en/articles/10408842
- https://help.openai.com/en/articles/10948259-google-drive-app-with-sync-self-service-setup

## 5. Create your private Drive root folder

In your Google Drive, create a folder named exactly:

`OPRA UAPP Presets`

You may also ask ChatGPT to create it after Google Drive write actions are connected.

The folder can remain **private**. It does not need to be shared publicly, with GitHub, or with the upstream project owner.

The converter's managed paths are created underneath this root, for example:

`OPRA UAPP Presets / Sennheiser / HD650`

A model folder may contain presets directly and also contain variant subfolders. That is intentional. For example, the upstream configuration contains an unclassified EW300 measurement directly in `SIMGOT/EW300` plus Gold, Silver, and DSP child folders.

## 6. Create a ChatGPT Project for your fork

Create a ChatGPT Project for this preset library and copy the instructions from:

`docs/CHATGPT_PROJECT_INSTRUCTIONS.md`

Before using them, replace the fixed GitHub repository value with your own fork:

`YOUR_GITHUB_USERNAME/opra-uapp-converter`

Keep the Drive root as:

`OPRA UAPP Presets`

Then test the setup with:

`What headphones do I have configured?`

ChatGPT should read your fork's `config/targets.json`.

Then test Drive access with:

`Is Drive up to date?`

ChatGPT should compare your fork's current manifest/output with **your** `OPRA UAPP Presets` folder.

## 7. Understand the completeness safeguard before customizing

The project deliberately defaults to **bringing over every usable OPRA parametric EQ profile** for a configured logical product.

This includes checking formatting-only OPRA product aliases. For example, if OPRA stores `Model X` and `Model-X` as separate records but their normalized names collide, the converter audits profiles across both records instead of trusting only the first one found.

The build fails when a complete product has a profile that is not routed anywhere or when one profile is routed into multiple folders. This is intentional.

A red coverage error usually means one of these things:

- OPRA added a new profile;
- a formatting-only alias contains additional profiles;
- a new/changed variant does not fit the current folder rules;
- a broad rule overlaps another variant rule.

Do not bypass the error automatically. Inspect the profile first.

If the intended folder is obvious from OPRA metadata, update the config. If the profile is ambiguous, ChatGPT should ask you what you want before assigning a folder.

Only use `allow_partial: true` when you explicitly want a subset. For example, if you say "add only the red variant," a partial configuration is appropriate. It should not be used merely to hide missing profiles.

## 8. Customize the headphones in your fork

The fork initially contains the upstream project's configured headphones. Remove any you do not want and add your own.

The easiest request is:

`Add the FiiO FT1 to my presets`

For a normal addition, ChatGPT should:

1. inspect OPRA and formatting-only aliases;
2. inventory every usable parametric EQ;
3. classify identifiable variants;
4. ask you only when a profile cannot be classified safely;
5. update `config/targets.json`;
6. verify a green GitHub build with complete coverage;
7. mirror the resulting XML files and root manifest into your Drive.

See `docs/ADDING_HEADPHONES.md` for config details including `include_terms`, exact `include_eq_ids`, and intentional `allow_partial` subsets.

## 9. What happens when OPRA changes later

The scheduled GitHub build re-runs coverage validation against the current OPRA feed.

If OPRA adds a profile that your existing complete routing does not cover, the build turns red instead of silently dropping it or guessing a folder. When you ask ChatGPT to check the failure, it should inspect the new profile and either update an unambiguous rule or ask you for a classification choice.

This is a safety feature. It keeps your library complete without inventing metadata.

## 10. Optional recurring Drive sync

The GitHub Action updates the generated GitHub output automatically. Google Drive mirroring is a separate ChatGPT-connected workflow because the repository intentionally stores **no Google credentials**.

If your ChatGPT environment supports scheduled tasks with connected apps, create a recurring task that:

1. checks that the latest `Update OPRA presets` workflow on your fork succeeded;
2. reads `config/targets.json` and `output/manifest.json` from your fork;
3. confirms complete products have no unmatched profiles/errors;
4. compares the managed files with your private `OPRA UAPP Presets` folder;
5. mirrors only the required additions/updates/removals at the correct managed folder level;
6. updates the Drive root `manifest.json`;
7. does nothing when Drive is already current.

The recurring task is only a safety net. When you add a headphone interactively, ChatGPT should sync the affected Drive files immediately when write actions are available.

## Privacy summary

- Your public fork contains converter code, configuration, generated EQ presets, and OPRA attribution.
- Your Google Drive remains governed by your Google sharing permissions.
- Making or using a public fork does **not** make your Drive public.
- Do not commit Google credentials, OAuth tokens, service-account files, or private Drive links/IDs to GitHub.
- Each user connects ChatGPT separately to their own GitHub account/fork and their own Google account/Drive.
- Profile/folder ambiguity should be resolved through explicit config/user choices, never through credentials or hidden external state.
