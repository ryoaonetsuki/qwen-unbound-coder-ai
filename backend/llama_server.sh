#!/usr/bin/env bash
# Start llama-server for the exact requested model. Edit only the variables.
# Single T4/P100: Q4_K_M will NOT fully fit (see docs/FEASIBILITY.md).
#   Use --ngl partial offload, or switch MODEL_FILE to IQ2_M, or use Kaggle dual-T4
#   with TENSOR_SPLIT="0.5,0.5" (llama-server -ts) — only with your approval.
set -euo pipefail
MODEL_FILE="${MODEL_FILE:-models/Qwen3.8-27B-Uncensored-Q4_K_M.gguf}"
CTX="${CTX:-8192}"
NGL="${NGL:-99}"            # 99 = full offload; lower = partial offload to CPU RAM
TENSOR_SPLIT="${TENSOR_SPLIT:-}"  # e.g. "0.5,0.5" on Kaggle dual T4
PORT="${LLAMA_PORT:-8080}"
EXTRA=()
if [ -n "$TENSOR_SPLIT" ]; then EXTRA+=(--tensor-split "$TENSOR_SPLIT"); fi
# The GGUF embeds the Qwen chat template; llama-server uses it automatically.
# MTP (fused file): --spec-type draft-mtp, per the model card. Skip it on old builds.
exec llama-server -m "$MODEL_FILE" --spec-type draft-mtp --spec-draft-n-max 2 \
  -ngl "$NGL" -c "$CTX" --port "$PORT" --host 127.0.0.1 "${EXTRA[@]}"
