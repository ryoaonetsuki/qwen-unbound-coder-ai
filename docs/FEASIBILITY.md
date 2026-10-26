# Feasibility — verified, not assumed (checked 2026-10-26)

## Exact model — VERIFIED EXISTS
- Repo: https://huggingface.co/JonathanColetti/Qwen3.8-27B-Uncensored-GGUF
- Base: https://huggingface.co/Qwen/Qwen3.8-27B — Apache 2.0, inherited by the derivative.
- File: `Qwen3.8-27B-Uncensored-Q4_K_M.gguf` = **16.8 GB**, MTP fused, 65 blocks.
  Other files in the same repo: IQ2_M 10.6 GB, IQ4_XS 15.3 GB, Q5_K_M 19.5 GB,
  Q6_K 22.4 GB, Q8_0 29.0 GB, noMTP-Q4_K_M 16.5 GB, mmproj F16 0.9 GB.
- Architecture: 64 layers = 48 Gated DeltaNet + 16 Gated Attention, hidden 5120,
  FFN 17408, vocab 248320, native context 262144.
- Refusal: publisher's own measurement, non-thinking mode, 100 held-out harmful
  prompts: base 98/100 refusals, this model 12/100. Reduced, **not eliminated**,
  and not measured for benign prompts or for the quantized files.
- Inference: llama.cpp `llama-server -m <file> --spec-type draft-mtp -ngl 99 -c 8192`
  (model card's own command; MTP needs a build newer than llama.cpp PR #22673).

## VRAM maths — why a single free T4/P100 does NOT fully fit Q4_K_M
Only the 16 full-attention layers keep a classic KV cache. At q8_0 KV that is
16 × 4 KV heads × 256 × 2 (K+V) × 1 byte = 32 KB per token.
- 8,192 ctx: KV 0.27 GB → weights 16.8 + ~1.5 GB CUDA/buffer overhead + KV ≈ **18.6 GB**
- 32,768 ctx: ≈ **19.4 GB**
- 262,144 ctx: KV 8.6 GB → ≈ **26.9 GB** (so this project defaults to 8,192 ctx)

Free Colab GPU is normally a T4 with ~15 GB usable VRAM; Kaggle's single P100
is 16 GB. **18.6 > 15/16, so full offload (-ngl 99) fails on one free card.**
That is a hard number, not a guess. Options, none applied silently:
1. **Kaggle dual T4 (2×16 GB ≈ 30 GB usable)** with llama-server tensor-split
   (`--tensor-split 0.5,0.5`): weights split ~8.4 GB per card, 18.6 GB total fits
   at 8k ctx. This is the only free path that keeps exact Q4_K_M fully on GPU,
   but Kaggle notebooks are session-based (reported ~12 h session, ~30 h/week
   GPU quota — check your own account page, quotas float), internet/tunnel
   behaviour is not guaranteed, and sharding must be tested on the real run.
2. **Partial offload on a single T4**: lower `-ngl` (e.g. ~50/65 layers ≈ 12.9 GB
   on GPU, rest in CPU RAM). It can load, but the CPU-resident layers make
   generation slow, and Colab free CPU RAM (~12.7 GB) is tight.
3. **IQ2_M (10.6 GB)**: ≈ 12.4 GB total at 8k ctx — fits a single T4 fully.
   Trade-off, stated by the publisher: IQ2_M is the most degraded file, and
   refusal behaviour at 2-bit is unmeasured. Needs your explicit approval.
4. **Paid / larger GPU** (e.g. Colab Pro L4 24 GB / A100 40 GB): contradicts the
   $0 requirement, so it is listed only for completeness, not recommended.

## Other platforms — checked
- **GitHub Actions**: free hosted runners have no GPU; GPU runners are paid.
  Used here only for tests/lint/deployment, never as a server.
- **Cloudflare Workers / Pages**: Workers cannot load a 16.8 GB GGUF; Workers AI
  is a catalog-only managed service (you pick a `@cf/` model, you do not upload
  a GGUF). Pages hosts only the static frontend in this project.
- **Colab / Kaggle**: not persistent servers. Sessions end, idle runtimes time
  out, quotas are dynamic and (in Salman's own recent experience) can be
  exhausted for ~18 hours. No 24/7 promise is made anywhere in this project.

## What was NOT verified here
No real Q4_K_M generation was run in this build: this VM has ~0.5 GB free RAM
and no GPU, and downloading 16.8 GB to a machine that cannot load it would
prove nothing. `scripts/test_live.py` is the test to run on the real notebook
run; until its output is pasted, the honest status is **code tested, model untested**.
