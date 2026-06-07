# Get the DeHowl app WITHOUT using Terminal or Xcode

You don't need to install anything on your Mac. GitHub's servers (which are
real Macs) will compile the app for you, and you download the finished
DeHowl.app from your browser. Everything below happens on github.com.

Total time: ~15 minutes, mostly waiting.

---

## Step 1 — Create a free GitHub account (skip if you have one)

Go to https://github.com and sign up. The free plan is enough — builds are
unlimited for public repositories.

## Step 2 — Create a new repository

1. Click the **+** (top right) → **New repository**
2. Name it `dehowl`
3. Choose **Public** (this makes the builds free and unlimited)
4. Tick **"Add a README file"**
5. Click **Create repository**

## Step 3 — Upload the project files

1. First, unzip the DeHowl source zip on your computer (just double-click it).
2. In your new repository, click **Add file → Upload files**.
3. Drag these items from the unzipped folder into the upload area:
   - `CMakeLists.txt`
   - the whole `Source` folder (drag the folder itself)
   - the whole `Assets` folder (drag the folder itself)
   Your browser keeps the folder structure automatically.
4. Click **Commit changes**.

## Step 4 — Add the build recipe

(The `.github` folder is hidden on Macs, so it's easier to create this file
directly on the website.)

1. In the repository, click **Add file → Create new file**
2. In the filename box, type exactly:

       .github/workflows/build-macos.yml

   (typing the `/` characters creates the folders automatically)
3. Open the file `github-workflow-COPY-THIS.txt` from the unzipped folder,
   copy ALL of its contents, and paste into the big text box on GitHub.
4. Click **Commit changes**.

The build starts automatically the moment you commit.

## Step 5 — Download your finished app

1. Click the **Actions** tab at the top of the repository.
2. You'll see a run called "Build DeHowl macOS app" with a yellow spinner.
   Wait ~10 minutes until it turns into a green check mark. (Refresh the page.)
3. Click the run, scroll down to **Artifacts**, and click **DeHowl-macOS**
   to download it.
4. Unzip the download (double-click). Inside is another zip — unzip that too.
   You now have **DeHowl.app**.

## Step 6 — Install and first launch

1. Drag **DeHowl.app** into your **Applications** folder.
2. Double-click it. macOS will block it the first time because it was
   downloaded from the internet ("Apple could not verify..."). Click **Done**.
3. Open **System Settings → Privacy & Security**, scroll down — you'll see
   *"DeHowl was blocked..."* — click **Open Anyway**, then confirm.
4. That's it. This only happens once. Allow microphone access when asked,
   then click **Audio Devices** inside the app to pick your interface.

---

## Updating the app later

Any time the source files change (e.g., you upload a new version of a file in
`Source/` via **Add file → Upload files**), GitHub automatically rebuilds.
Just go back to **Actions** and download the new artifact.

## Notes

- The app is built **universal**: it runs natively on both Apple Silicon
  (M1/M2/M3/M4) and older Intel Macs.
- The "Open Anyway" step exists because the app isn't notarized with a paid
  Apple Developer account ($99/yr). If you ever want to distribute DeHowl to
  many people without that warning, an Apple Developer membership + 
  notarization can be added to this same build recipe later.
