#!/usr/bin/env bash
# Build linux/amd64 image (runs on Linux / Windows / macOS Docker hosts).
set -euo pipefail
cd "$(dirname "$0")"
TAG="${1:-faceplugin/face-liveness:local}"

LIB_RELEASE="https://github.com/Faceplugin-ltd/FaceLivenessDetection-Docker/releases/tag/latest"

if [[ ! -f lib/cpu/libFaceLivenessSDK.so ]] \
  || [[ ! -f lib/cpu/libfacerec.so ]] \
  || [[ ! -f lib/cpu/fal.fpk ]] \
  || [[ ! -f lib/cpu/libonnxruntime.so ]] \
  || [[ ! -f lib/cpu/libonnxruntime_providers_shared.so ]]; then
  echo "ERROR: ./lib/cpu/ is incomplete."
  echo "Need: libFaceLivenessSDK.so, libfacerec.so, fal.fpk, libonnxruntime.so, libonnxruntime_providers_shared.so"
  echo "Download runtime.zip and extract it into ./lib/cpu/:"
  echo "  $LIB_RELEASE"
  exit 1
fi

docker build --platform linux/amd64 -t "$TAG" .
echo "Built $TAG (linux/amd64)"
