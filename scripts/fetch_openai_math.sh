#!/usr/bin/env bash
# Optional sparse checkout of github.com/openai/math without full PDF tree.
# Default: clone to ./vendor/openai-math-sparse (gitignored pattern: vendor/).
# For full corpus use: git submodule update --init research/external/openai-math
set -euo pipefail

REPO_URL="${OPENAI_MATH_URL:-https://github.com/openai/math.git}"
PIN="${OPENAI_MATH_PIN:-adc7f1241b42e322a6451854ab7e4b4c146bf78a}"
DEST="${OPENAI_MATH_DEST:-vendor/openai-math-sparse}"

# Space-separated cone paths (no preprints PDF bulk)
SPARSE_PATHS="${OPENAI_MATH_SPARSE:-CONTENTS.md overview.pdf lean README.md LICENSE}"

if [[ -d "$DEST/.git" ]]; then
  echo "Updating existing sparse clone at $DEST"
  git -C "$DEST" fetch --depth 1 origin "$PIN" || git -C "$DEST" fetch origin "$PIN"
  git -C "$DEST" checkout "$PIN"
else
  echo "Creating sparse clone at $DEST (pin $PIN)"
  git clone --filter=blob:none --sparse "$REPO_URL" "$DEST"
  git -C "$DEST" checkout "$PIN"
fi

git -C "$DEST" sparse-checkout set $SPARSE_PATHS
echo "Sparse tree ready. Add preprints/ only if you need PDFs:"
echo "  git -C $DEST sparse-checkout add preprints/<family-dir>"
