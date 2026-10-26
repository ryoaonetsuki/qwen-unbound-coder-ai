# Qwen Unbound Coder AI

A free, open-weight coding assistant built around one exact, verified model —
**not** a demo with canned replies. If the model backend is offline, the
frontend says so and refuses to fake an answer.

- **Product:** Qwen Unbound Coder AI
- **Creator:** Salman Biswas
- **Developer identity:** Ryo Aonetsuki
- **GitHub:** https://github.com/ryoaonetsuki
- **Telegram:** https://t.me/ryoaonetsuki
- **Channel:** https://t.me/aonetsukiarchive (@aonetsukiarchive)
- **Repo context:** https://github.com/ryoaonetsuki/salman-dev-app (this project
  is an independent, forkable repo of its own)

## Model — verified 2026-10-26

| Item | Value |
|---|---|
| Repo | https://huggingface.co/JonathanColetti/Qwen3.8-27B-Uncensored-GGUF |
| Base | https://huggingface.co/Qwen/Qwen3.8-27B |
| File | `Qwen3.8-27B-Uncensored-Q4_K_M.gguf` — **16.8 GB** |
| Licence | Apache 2.0, inherited from the base model |
| Architecture | 64 layers (48 Gated DeltaNet + 16 Gated Attention), hidden 5120, vocab 248320, native context 262144 |
| Engine | llama.cpp `llama-server`, MTP via `--spec-type draft-mtp` |
| Chat template | Embedded in the GGUF; llama-server applies it automatically |
| Reduced refusal | Publisher-measured 12/100 vs base 98/100 on one 100-prompt harmful set, non-thinking mode. Reduced, not eliminated. |

## ⚠️ Read this before you start — the honest blocker

**Q4_K_M does NOT fully fit a single free Colab T4 (~15 GB usable) or Kaggle
P100 (16 GB).** At the project's default 8,192-token context it needs about
**18.6 GB** (16.8 weights + ~1.5 overhead + 0.27 KV cache). Full offload will
fail on one free card. See `docs/FEASIBILITY.md` for the full maths.

Free paths that keep the *exact* model, in order of promise:
1. **Kaggle dual T4** (2×16 GB) with tensor-split — the only free path that can
   hold Q4_K_M fully on GPU. Must be tested on a real Kaggle run.
2. **Colab single T4, partial offload** (`NGL=50`) — loads, but slower.
3. **IQ2_M (10.6 GB)** on a single T4 — fits, but is the most degraded quant
   and its refusal behaviour is unmeasured. **This needs your explicit
   approval; it is NOT the default and was NOT silently substituted.**

No 24/7 uptime is promised. Colab/Kaggle sessions end, idle runtimes time out,
and quotas can be exhausted. This is an occasional-use assistant with a
simple phone restart workflow.

## Architecture

```
Phone browser ──► Static frontend (GitHub/Cloudflare Pages)
                      │  (tunnel URL + gateway key, set by you)
                      ▼
              Notebook gateway (Python stdlib, port 8000)
                      │  auth + validation, 503 when backend is down
                      ▼
              llama-server (127.0.0.1:8080, real GGUF inference)
```

- GitHub Actions: tests and deployment only — free runners have no GPU.
- Cloudflare Workers AI: catalog-only, cannot run this GGUF — not used for
  inference. Cloudflare Pages is used only for the static frontend.
- No chat history is stored by default. No database is required.

## Quick start (Android)

Full steps: `docs/ANDROID_SETUP.md`. Short version:

1. Create your own public repo from this ZIP and host `frontend/index.html`
   (GitHub Pages or Cloudflare Pages).
2. Open `notebooks/qwen-unbound-coder-colab.ipynb` (or the Kaggle one) on
   your phone, choose GPU, run all cells.
3. Install llama.cpp: `bash backend/install_llama.sh cuda-12.4` (or cpu).
4. Wait for `/health` to report `backend_reachable: true`, copy the tunnel
   URL into the frontend, press Reconnect, chat.

## Files

- `frontend/index.html` — mobile-first dark UI, Markdown + code highlighting,
  copy-code buttons, streaming, health/reconnect, creator credits.
- `backend/gateway.py` — stdlib-only OpenAI-compatible gateway (health,
  models, chat completions, streaming, auth, validation).
- `backend/llama_server.sh` — llama-server launch for the exact model.
- `backend/install_llama.sh` — fetch a current llama.cpp release binary.
- `scripts/download_model.py` — resumable download of the exact GGUF.
- `scripts/test_live.py` — real-model smoke test (fails on empty replies).
- `tests/test_gateway.py` — gateway auth/validation/proxy tests (fake
  upstream only — they do NOT prove the real model works).
- `notebooks/` — Colab + Kaggle notebooks (7 cells each).
- `docs/FEASIBILITY.md`, `docs/ANDROID_SETUP.md`, `docs/SECURITY.md`.

## Tests run in this build (honest scope)

- Gateway unit tests: **pass** (see below) — auth, validation, proxy logic
  against a local fake upstream.
- Frontend: loads, contains creator links, health-check logic present.
- **NOT run:** real Q4_K_M generation. This build machine has no GPU and
  ~0.5 GB free RAM, so downloading 16.8 GB there would prove nothing.
  Run `scripts/test_live.py` on the notebook and paste its output before
  claiming the model works.

## Licence

Apache 2.0 (`LICENSE`), inherited from Qwen/Qwen3.8-27B. The base model's
licence and acceptable-use terms still apply to this derivative.
