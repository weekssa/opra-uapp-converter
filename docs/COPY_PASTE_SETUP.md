# Copy/paste setup walkthrough

This project can be used in two different ways. Pick the path that matches what you want.

## Path A — I only want the presets that are already published

**No fork, ChatGPT Project, or Google Drive connection is required.**

1. Open this repository's **Releases** page.
2. Open the newest release.
3. Download `opra-uapp-presets-vX.Y.Z.zip` from **Assets**.
4. Extract the ZIP on your computer or Android device.
5. Find the XML preset for your headphone under its manufacturer/model folder.
6. Put the XML somewhere your Android device can access. Google Drive is optional.
7. Import the XML as a ToneBoosters/UAPP preset on the device where you use USB Audio Player PRO.

The release also contains `manifest.json` for OPRA creator/source attribution and a `.sha256` file for verifying the ZIP if desired.

If the headphone you want is already included in the release, you can stop here.

---

## Path B — I want my own automatically maintained headphone library

For a personalized library, **fork this repository first**. Your fork becomes the source of truth for your headphones, generated presets, version history, and releases. Your Google Drive remains separate and can stay private.

You do not need Python, Terminal, a GitHub personal access token, or Google credentials stored in GitHub.

### Step 1 — Fork the repository

In GitHub:

1. Open `weekssa/opra-uapp-converter`.
2. Click **Fork**.
3. Choose your GitHub account.
4. Keep the repository name `opra-uapp-converter` unless you have a reason to change it.
5. Create the fork.

Your repository will normally be:

```text
YOUR_GITHUB_USERNAME/opra-uapp-converter
```

### Step 2 — Enable the automatic GitHub build

In **your fork**:

1. Open **Actions**.
2. Enable Actions/workflows if GitHub asks.
3. Open **Update OPRA presets**.
4. Enable the workflow if needed.
5. Run it once from `main`.
6. Confirm the run finishes green.

The workflow uses GitHub's normal short-lived Actions token. Do not create a personal access token for this setup.

### Step 3 — Connect GitHub and Google Drive to ChatGPT

In ChatGPT, open the app/plugin settings for your account. The exact label can vary by ChatGPT surface, but GitHub and Google Drive are connected from the ChatGPT app/plugin directory.

Connect **GitHub** and authorize your fork:

```text
YOUR_GITHUB_USERNAME/opra-uapp-converter
```

Connect **Google Drive** using the Google account that should own your preset library.

For automatic Drive mirroring, the Google Drive connection must offer file/folder write actions. If your plan, workspace, region, or device only exposes read access, ChatGPT can still inspect the library but cannot automatically upload the XML files.

Do not paste Google passwords, OAuth tokens, GitHub tokens, or Drive credentials into ChatGPT Project Instructions or into the repository.

### Step 4 — Create the private Drive folder

In your Google Drive, create exactly:

```text
OPRA UAPP Presets
```

It can remain private. It does not need to be shared publicly or with GitHub.

### Step 5 — Create a ChatGPT Project

Create a new ChatGPT Project for the preset library.

Open the project's **Project settings** and find **Project instructions**.

Now open this file in **your fork**:

```text
docs/CHATGPT_PROJECT_INSTRUCTIONS.md
```

Copy the entire contents into the Project Instructions box.

Before saving, replace:

```text
YOUR_GITHUB_USERNAME/opra-uapp-converter
```

with your actual fork, for example:

```text
alexsmith/opra-uapp-converter
```

Leave the Drive root as:

```text
OPRA UAPP Presets
```

Save the Project instructions.

### Step 6 — Copy/paste this setup check into your first Project chat

Replace the example repository with your own fork, then paste this message:

```text
Set up and verify my OPRA UAPP preset project. Do not add or remove any headphones yet.

My repository is:
YOUR_GITHUB_USERNAME/opra-uapp-converter

My Google Drive root is:
OPRA UAPP Presets

Please:
1. Read the current repository instructions/runbook, config/targets.json, docs/AUTOMATION.md, VERSION, and output/manifest.json.
2. Confirm you can read my fork rather than the upstream repository.
3. Confirm the latest Update OPRA presets GitHub Action succeeded.
4. Confirm the current project version and number of generated presets.
5. Check whether you have Google Drive write actions available.
6. If Drive writes are available, inspect OPRA UAPP Presets and tell me whether it is currently synchronized.
7. Do not change config, GitHub files, or Drive files unless a difference must be fixed to complete this setup check. Tell me before any unexpected destructive change.
8. Finish with a short READY / NEEDS ATTENTION summary and tell me exactly what, if anything, I still need to do manually.
```

A successful result should confirm that ChatGPT is reading **your fork**, that GitHub Actions is healthy, and whether your Drive connection can be maintained automatically.

### Step 7 — Add your first headphone

Once setup is verified, paste something like:

```text
Add the FiiO FT1 to my presets.
```

ChatGPT should **not** immediately import everything. It should first verify the exact OPRA product, enumerate all usable parametric EQ profiles, cross-check the supported OPRA feed, and show you the complete candidate list.

Then reply with your choice, for example:

```text
Import all
```

or:

```text
Only 1, 3, and 5
```

or:

```text
All except 2
```

After approval, ChatGPT should update only the required target configuration, wait for the GitHub build, verify the manifest/version/release, and sync the generated XML files to your Drive when write actions are available.

### Step 8 — Copy/paste these useful maintenance commands later

```text
What headphones do I have configured?
```

```text
Check for new presets
```

```text
Sync Drive now
```

```text
Is Drive up to date?
```

```text
Remove [headphone]
```

### Step 9 — Use the presets on your Android/UAPP device

Your managed Drive layout will look like:

```text
OPRA UAPP Presets/
└── Manufacturer/
    └── Model/
        └── preset.xml
```

On the Android device where you use UAPP:

1. Open the connected Google Drive account or otherwise make the desired XML available locally.
2. Choose the XML for the headphone/variant you want.
3. Import that XML into UAPP's ToneBoosters preset system.
4. The embedded preset name is headphone-first, so it should be recognizable in UAPP even when the folder path is not shown.

The GitHub/ChatGPT setup does not have to be repeated on every device. Your ChatGPT Project and GitHub fork remain the maintained source, while Drive is the convenient bridge to Android/UAPP.

---

## What belongs to whom?

- **Upstream repository:** the original converter and public releases.
- **Your fork:** your configured headphones, generated output, version history, tags, and releases.
- **Your Google Drive:** your private mirrored preset library.
- **Your ChatGPT Project:** the maintenance instructions and conversations that coordinate your fork and Drive.

A public GitHub fork does **not** make your Google Drive public.

## More detailed help

For the longer explanation and troubleshooting steps, see:

- [`NEW_USER_SETUP.md`](NEW_USER_SETUP.md)
- [`CHATGPT_PROJECT_INSTRUCTIONS.md`](CHATGPT_PROJECT_INSTRUCTIONS.md)
- [`ADDING_HEADPHONES.md`](ADDING_HEADPHONES.md)
- [`AUTOMATION.md`](AUTOMATION.md)
