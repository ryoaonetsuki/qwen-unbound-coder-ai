#!/usr/bin/env python3
"""Download (resumable) the exact GGUF file. No credentials are stored here.
Usage: python3 scripts/download_model.py [--quant Q4_K_M|IQ2_M|IQ4_XS] [--dir models]
Default quant is the requested Q4_K_M. Changing --quant is a deliberate
substitution, not a silent default — see docs/FEASIBILITY.md first.
"""
import argparse, os, sys, urllib.request

REPO = "JonathanColetti/Qwen3.8-27B-Uncensored-GGUF"
FILES = {
    "Q4_K_M": "Qwen3.8-27B-Uncensored-Q4_K_M.gguf",
    "IQ4_XS": "Qwen3.8-27B-Uncensored-IQ4_XS.gguf",
    "IQ2_M": "Qwen3.8-27B-Uncensored-IQ2_M.gguf",
    "noMTP-Q4_K_M": "Qwen3.8-27B-Uncensored-noMTP-Q4_K_M.gguf",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quant", default="Q4_K_M", choices=list(FILES))
    ap.add_argument("--dir", default="models")
    args = ap.parse_args()
    name = FILES[args.quant]
    os.makedirs(args.dir, exist_ok=True)
    dest = os.path.join(args.dir, name)
    url = f"https://huggingface.co/{REPO}/resolve/main/{name}"
    print(f"Downloading {url}\n  -> {dest}  (resumable with -C via curl is preferred in notebooks)")
    # Use curl when available for resume; fall back to urllib.
    import shutil, subprocess
    if shutil.which("curl"):
        subprocess.run(["curl", "-L", "-C", "-", "-o", dest, url], check=True)
    else:
        urllib.request.urlretrieve(url, dest)
    print(f"Done: {dest} ({os.path.getsize(dest)/1e9:.2f} GB)")
    print("Verify size against the model card before starting llama-server.")

if __name__ == "__main__":
    main()
