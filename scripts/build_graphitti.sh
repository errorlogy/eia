#!/usr/bin/env bash
# M-GRAPHITTI-CI — build Graphitti CPU binary and run test-tiny.xml smoke.
# Usage: bash scripts/build_graphitti.sh
# Requires: cmake >=3.12, g++ (C++17), libboost-graph-dev (Ubuntu/Debian).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GRAPHITTI="${REPO_ROOT}/research/vendor/graphitti"
BUILD_DIR="${GRAPHITTI}/build"
CONFIG="../configfiles/test-tiny.xml"
JOBS="${GRAPHITTI_BUILD_JOBS:-$(nproc 2>/dev/null || echo 2)}"

echo "==> Graphitti build (ENABLE_CUDA=NO)"
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

if [[ ! -f CMakeCache.txt ]]; then
  cmake -D ENABLE_CUDA=NO ..
fi
make -j"${JOBS}"

if [[ ! -x ./cgraphitti ]]; then
  echo "build_graphitti: cgraphitti binary missing after make" >&2
  exit 1
fi

echo "==> Run test-tiny.xml"
./cgraphitti -c "${CONFIG}"
OUTPUT_XML="${BUILD_DIR}/Output/Results/test-tiny-out.xml"
if [[ ! -f "${OUTPUT_XML}" ]]; then
  echo "build_graphitti: expected output ${OUTPUT_XML}" >&2
  exit 1
fi

echo "build_graphitti: OK (binary=${BUILD_DIR}/cgraphitti output=${OUTPUT_XML})"
