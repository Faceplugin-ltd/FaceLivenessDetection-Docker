#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Inside Docker, a plain `docker run` has the container's own /etc/machine-id.
# The license is then bound to that id, not the host, and will not match later.
require_docker_launch() {
  [[ -f /.dockerenv ]] || return 0
  local ok=1
  local cap shm_kb
  if ! mountpoint -q /etc/machine-id; then
    ok=0
  fi
  shm_kb="$(df -k /dev/shm | awk 'NR==2 {print $2}')"
  if [[ "${shm_kb:-0}" -lt 1900000 ]]; then
    ok=0
  fi
  # Privileged sets CAP_SYS_ADMIN. A normal docker run does not.
  if ! python3 -c 'import pathlib; c=int(pathlib.Path("/proc/1/status").read_text().split("CapEff:")[1].split()[0], 16); raise SystemExit(0 if c & (1 << 21) else 1)'; then
    ok=0
  fi
  if [[ "$ok" -eq 1 ]]; then
    return 0
  fi
  echo "ERROR: Do not start this image with a plain docker run." >&2
  echo "That uses the container's own machine id, so the license machine code is wrong." >&2
  echo >&2
  echo "Start it with the host machine id, 2GB shared memory, and privileged mode:" >&2
  echo >&2
  echo "docker run -d --name faceplugin-face-liveness \\" >&2
  echo "  --shm-size=2gb --privileged \\" >&2
  echo "  -p 8093:8093 \\" >&2
  echo "  -v /etc/machine-id:/etc/machine-id:ro \\" >&2
  echo "  faceplugin/face-liveness:latest" >&2
  exit 1
}

require_docker_launch

# The release page holds one archive, runtime.zip.
LIB_RELEASE="https://github.com/Faceplugin-ltd/FaceLivenessDetection-Docker/releases/tag/latest"

if [[ ! -f lib/cpu/libFaceLivenessSDK.so ]] \
  || [[ ! -f lib/cpu/libfacerec.so ]] \
  || [[ ! -f lib/cpu/fal.fpk ]] \
  || [[ ! -f lib/cpu/libonnxruntime.so ]] \
  || [[ ! -f lib/cpu/libonnxruntime_providers_shared.so ]]; then
  echo "ERROR: ./lib/cpu/ is incomplete."
  echo "Download runtime.zip and extract it into ./lib/cpu/:"
  echo "  $LIB_RELEASE"
  exit 1
fi

export LICENSE="${LICENSE:-$(pwd)/license.txt}"
export LD_LIBRARY_PATH="$(pwd)/lib/cpu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PORT="${PORT:-${FACESDK_PORT:-8093}}"
exec python3 app.py
