#!/usr/bin/env bash
# Fetch a current llama.cpp release binary. Fails loudly if the asset layout
# changed — do not guess a URL and pretend it worked.
# Usage: bash backend/install_llama.sh [cuda-12.4|cpu]
set -euo pipefail
MODE="${1:-cuda-12.4}"
TAG="$(curl -s https://api.github.com/repos/ggml-org/llama.cpp/releases/latest | grep -m1 '"tag_name"' | cut -d'"' -f4)"
[ -n "$TAG" ] || { echo "ERROR: could not read latest llama.cpp release tag"; exit 1; }
echo "Latest llama.cpp release: $TAG"
if [ "$MODE" = "cpu" ]; then PATTERN="bin-ubuntu-x64"; else PATTERN="bin-ubuntu-cuda-12.4-x64"; fi
ASSET="$(curl -s "https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/$TAG" | grep '"name"' | grep "$PATTERN" | head -1 | cut -d'"' -f4)"
[ -n "$ASSET" ] || { echo "ERROR: no $PATTERN asset in $TAG — check the releases page manually"; exit 1; }
curl -L -o llama.tar.gz "https://github.com/ggml-org/llama.cpp/releases/download/$TAG/$ASSET"
mkdir -p llama-bin && tar xzf llama.tar.gz -C llama-bin --strip-components=1
ls llama-bin/bin/llama-server
echo "Add to PATH: export PATH=\$PWD/llama-bin/bin:\$PATH"
