# Android-only setup & restart (no computer needed)

## 1. Create the repo (once, from your phone)
1. On github.com, create a new **public** repo, e.g. `qwen-unbound-coder-ai`.
   Do NOT paste any key into the repo.
2. Upload the ZIP contents (or push from the GitHub web UI / mobile app).
3. Settings → Pages → Deploy from branch → `main` → `/frontend` is NOT a GitHub
   Pages source, so instead: keep the frontend at repo root for Pages, or use
   Cloudflare Pages with build output = `frontend`. Simplest phone path:
   GitHub Pages from `main` branch, root folder, after copying
   `frontend/index.html` to the repo root as `index.html` (the file is
   self-contained; it works from either location).

## 2. Start the model (each session, from your phone)
1. Open the Colab notebook (`notebooks/qwen-unbound-coder-colab.ipynb`) in the
   Colab app/browser, or the Kaggle notebook on Kaggle.
2. Runtime → Change runtime type → GPU (T4). Colab: if it says GPU usage
   limits, stop — do not retry in a loop; wait and try later.
3. Run all cells. The notebook will: check `nvidia-smi`, download the 16.8 GB
   GGUF (first run only per session — Colab local files do NOT survive a new
   runtime; if you mounted Drive, the file can be cached there where permitted),
   start llama-server + the gateway, and print a tunnel URL.
4. Copy the tunnel URL into the frontend's Backend settings, set the same
   gateway key you chose in the notebook, press Reconnect.
5. Health must say **Online — real model** before you chat. If it says offline,
   the chat will refuse to fake a reply — check the notebook logs.

## 3. Stop
Runtime → Disconnect / Factory reset when done. This frees quota for next time.
Never leave a notebook idling to "keep it online" — free tiers disconnect
idle runtimes anyway, and it burns the quota you need later.

## 4. Forking (for a friend)
Fork the repo, use their own Colab/Kaggle account and their own gateway key.
Nothing in the repo is tied to Salman's accounts except the creator credits.
