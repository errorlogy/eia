#!/usr/bin/env bash
# M-GRAPHITTI-CI — build Graphitti CPU binary and run test-tiny.xml smoke.
# Usage: bash scripts/build_graphitti.sh
# Requires: cmake >=3.12, g++ (C++17), libboost-graph-dev (Ubuntu/Debian).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR_GRAPHITTI="${REPO_ROOT}/research/vendor/graphitti"
GRAPHITTI_PIN="${GRAPHITTI_PIN:-b96e96c32b11ae7fc5526da7f2c8452c903a28bf}"
GRAPHITTI_REPO="${GRAPHITTI_REPO:-https://github.com/UWB-Biocomputing/Graphitti.git}"
FULL_GRAPHITTI="${REPO_ROOT}/research/sci_flow/.ci-artifacts/graphitti-src"
BUILD_DIR_MARKER="${REPO_ROOT}/research/sci_flow/.ci-artifacts/graphitti-build-dir.txt"
CONFIG="../configfiles/test-tiny.xml"
JOBS="${GRAPHITTI_BUILD_JOBS:-$(nproc 2>/dev/null || echo 2)}"

resolve_graphitti_src() {
  if [[ -f "${VENDOR_GRAPHITTI}/Simulator/Core/Graphitti_Main.cpp" ]]; then
    printf '%s\n' "${VENDOR_GRAPHITTI}"
    return 0
  fi
  echo "==> Vendor snapshot incomplete; fetching Graphitti at ${GRAPHITTI_PIN}" >&2
  if [[ ! -f "${FULL_GRAPHITTI}/Simulator/Core/Graphitti_Main.cpp" ]]; then
    rm -rf "${FULL_GRAPHITTI}"
    git clone --depth 1 --branch master "${GRAPHITTI_REPO}" "${FULL_GRAPHITTI}"
    (
      cd "${FULL_GRAPHITTI}"
      git fetch --depth 1 origin "${GRAPHITTI_PIN}"
      git checkout "${GRAPHITTI_PIN}"
    )
  fi
  printf '%s\n' "${FULL_GRAPHITTI}"
}

bootstrap_googletest() {
  local graphitti_src="$1"
  local gtest_dir="${graphitti_src}/Testing/lib/googletest-master"
  local gtest_include_link="${graphitti_src}/Testing/lib/GoogleTest/googletest-master"
  if [[ -f "${gtest_dir}/CMakeLists.txt" ]]; then
    return 0
  fi
  echo "==> Bootstrap googletest (vendor snapshot omits Testing/lib)"
  mkdir -p "${graphitti_src}/Testing/lib"
  git clone --depth 1 --branch release-1.12.1 \
    https://github.com/google/googletest.git "${gtest_dir}"
  mkdir -p "${graphitti_src}/Testing/lib/GoogleTest"
  ln -sfn googletest-master "${gtest_include_link}"
}

GRAPHITTI="$(resolve_graphitti_src)"
BUILD_DIR="${GRAPHITTI}/build"
GTEST_DIR="${GRAPHITTI}/Testing/lib/googletest-master"

echo "==> Graphitti build (ENABLE_CUDA=NO) source=${GRAPHITTI}"
bootstrap_googletest "${GRAPHITTI}"
mkdir -p "${BUILD_DIR}"
printf '%s\n' "${BUILD_DIR}" > "${BUILD_DIR_MARKER}"
if [[ -n "${GITHUB_ENV:-}" ]]; then
  echo "GRAPHITTI_BUILD_DIR=${BUILD_DIR}" >> "${GITHUB_ENV}"
fi
cd "${BUILD_DIR}"

if [[ ! -f CMakeCache.txt ]]; then
  cmake -D ENABLE_CUDA=NO ..
fi
make -j"${JOBS}" cgraphitti

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
