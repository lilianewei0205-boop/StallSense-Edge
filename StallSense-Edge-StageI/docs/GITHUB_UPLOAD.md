# Publish this repository on GitHub

The zip delivered in ChatGPT is **not yet an actual GitHub repository**. Only after uploading does the competition-ready public URL exist.

1. Download and extract the `StallSense-Edge-StageI-GitHub.zip` file.
2. Sign in to GitHub and visit https://github.com/new .
3. Choose a repository name, for example `StallSense-Edge`; select **Public** unless your team has a reason not to. Do not initialize with a README because one is already included.
4. Create the repository. On its empty landing page, choose **uploading an existing file** (or `Add file` → `Upload files`).
5. Upload the **contents of the extracted folder**, not the ZIP itself; include the `stall_sense`, `tests`, `data`, `docs` and `.streamlit` directories (the browser may skip dot-directories; if so, add the optional theme config later). Never include a real `.env`, personal sales records, or local `.db` file.
6. Commit the files.
7. Copy the repository URL from the address bar; format: `https://github.com/YOUR-USERNAME/StallSense-Edge`. **Replace YOUR-USERNAME with your real GitHub username.**
8. Replace the placeholder on slide 17 of the proposal, and verify the link from a logged-out browser window.

Optional command-line route after creating the empty repository:

```bash
cd StallSense-Edge-StageI
git init
git add .
git commit -m "Stage I reproducible demo"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/StallSense-Edge.git
git push -u origin main
```

No command above has been executed on your GitHub account by the ChatGPT file generator.
