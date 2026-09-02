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

GTEST_DIR="${GRAPHITTI}/Testing/lib/googletest-master"
GTEST_INCLUDE_LINK="${GRAPHITTI}/Testing/lib/GoogleTest/googletest-master"

bootstrap_googletest() {
  if [[ -f "${GTEST_DIR}/CMakeLists.txt" ]]; then
    return 0
  fi
  echo "==> Bootstrap googletest (vendor snapshot omits Testing/lib)"
  mkdir -p "${GRAPHITTI}/Testing/lib"
  git clone --depth 1 --branch release-1.12.1 \
    https://github.com/google/googletest.git "${GTEST_DIR}"
  mkdir -p "${GRAPHITTI}/Testing/lib/GoogleTest"
  ln -sfn googletest-master "${GTEST_INCLUDE_LINK}"
}

echo "==> Graphitti build (ENABLE_CUDA=NO)"
bootstrap_googletest
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
