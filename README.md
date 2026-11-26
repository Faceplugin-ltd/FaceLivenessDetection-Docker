<div align="center">
<img alt="FacePlugin" src="https://raw.githubusercontent.com/Faceplugin-ltd/faceplugin-assets/main/brand/logo.png" width="400"/>
</div>

#### 🌐 Company Site - [Here](https://faceplugin.com)
#### 🤗 Hugging Face - [Here](https://huggingface.co/FacePlugin-Ltd)
#### 🛟 Help Center - [Here](https://doc.faceplugin.com)
#### 🐳 Docker Hub - [Here](https://hub.docker.com/r/faceplugin/face-liveness)

# FacePlugin Face Liveness Detection — Docker (Fully On-Premise)

Jump: [Quick start](#quick-start) · [Get the runtime](#get-the-runtime) · [Start the API](#start-the-api) · [SDK License](#sdk-license) · [Try it](#try-it) · [Setup on your own app](#setup-on-your-own-app) · [About SDK](#about-sdk)

## Quick start

- [ ] **Docker (recommended):** `docker pull faceplugin/face-liveness:latest`, then `docker run` — [Start the API](#option-a--docker)
- [ ] **Or native Linux:** download `runtime.zip` from [Releases](https://github.com/Faceplugin-ltd/FaceLivenessDetection-Docker/releases/tag/latest) and extract it into `lib/cpu/`, then `./run.sh` — [Get the runtime](#get-the-runtime)
- [ ] Confirm it is running: `curl -s http://127.0.0.1:8093/api/health` (no license needed yet)
- [ ] [Contact us](#contact) with your machine code for a license key, then `POST /api/activate`
- [ ] Try it with Postman, curl, or the Gradio demo on **9093** (`python3 demo.py`)

Docs: [doc.faceplugin.com](https://doc.faceplugin.com) · Try online: [Hugging Face Space](https://huggingface.co/spaces/FacePlugin-Ltd)

## Introduction

FacePlugin **Face Liveness Detection** is a fully on-premise anti-spoofing engine for KYC and remote identity verification. It answers one question about one photo — *is this a real face in front of the camera, or a presentation attack?* — and returns Real / Spoof with a score. **Passive**: nothing is asked of the person, and a single RGB frame is enough. No depth camera, no infrared, no extra hardware.

It detects printed photos, screen replays (photo and video), 3D masks, and deepfakes handled as one more kind of spoof.

The SDK runs as a REST API server through **Docker on a Linux host**, or natively on **Linux x86_64**. It runs on CPU only. The container is started privileged, with 2 GB of shared memory and the host's `/etc/machine-id` bound in — see [Option A — Docker](#option-a--docker) — so Docker Desktop on macOS or Windows is not a supported host; use a Linux VM there. This repository is self-contained; no other FacePlugin repository is required.

All processing stays on your server. **No** biometric data is sent to FacePlugin — built for banking, eKYC, and on-premise compliance workflows.

### Main Functionalities

| Feature | API |
| ------- | --- |
| **Passive face liveness** — score one RGB image for presentation attacks | `POST /api/liveness` · `sdk.liveness` |
| Printed photo, screen replay, 3D mask and deepfake detection | same call |
| Score, Real/Spoof verdict, pass flag | `data.score` · `data.result` · `data.pass` |
| Health / machine code / activate / license | `GET /api/health` · `GET /api/machinecode` · `POST /api/activate` · `GET /api/licenseStatus` |
| Which runtime is loaded | `GET /api/backend` |

Score **≥ 0.5** → `result: "Real"`, `pass: true`. Score **< 0.5** → `result: "Spoof"`, `pass: false`.

`POST /api/check_liveness` is an alias of `/api/liveness`. Routes are `/api/*`; there is no version segment, and every `/api/*` path answers `OPTIONS` for browser preflight.

The call takes one image and nothing else — there is **no model or algorithm to choose**. The runtime fuses every RGB estimator it holds into the single score you get back, and `pass` is `score >= 0.5`, fixed in native code and not settable over HTTP.

Liveness here is **passive only**. There is no active (challenge–response) liveness over HTTP; for that, use the mobile SDKs in [Product List](#product-list).

### Benchmarks

Passive mode, at the default threshold of **0.5**:

| Metric | This product (server) |
| ------ | --------------------- |
| **BPCER** — real faces wrongly rejected | **0%** (none observed) |
| **APCER** — attacks wrongly accepted | **0.5 – 1.5%** |

Measured by FacePlugin QA following the **ISO/IEC 30107-3** methodology, against four presentation attack instrument species: printed photo, screen replay (photo), screen replay (video), and a painted 3D resin mask.

> This is an **internal evaluation, not an independent laboratory result**, and no iBeta certification is claimed. A 0% BPCER means no rejection was *observed* — for 600 presentations the one-sided 95% upper bound is about 0.5%. Ask us for the full PAD evaluation report.

Figures: [doc.faceplugin.com](https://doc.faceplugin.com/products/face-recognition-sdk/liveness-detection-sdk).

### Product List

The same Face Liveness product ships on nine platforms. The mobile SDKs run on-device and offer **passive and active** liveness; the two server products are **passive only**.

| Platform | Repository |
| -------- | ---------- |
| Android | [FaceLivenessDetection-Android](https://github.com/Faceplugin-ltd/FaceLivenessDetection-Android) |
| iOS | [FaceLivenessDetection-iOS](https://github.com/Faceplugin-ltd/FaceLivenessDetection-iOS) |
| Flutter | [FaceLivenessDetection-Flutter](https://github.com/Faceplugin-ltd/FaceLivenessDetection-Flutter) |
| React Native | [FaceLivenessDetection-ReactNative](https://github.com/Faceplugin-ltd/FaceLivenessDetection-ReactNative) |
| Ionic Capacitor | [FaceLivenessDetection-Ionic-Capacitor](https://github.com/Faceplugin-ltd/FaceLivenessDetection-Ionic-Capacitor) |
| Ionic Cordova | [FaceLivenessDetection-Ionic-Cordova](https://github.com/Faceplugin-ltd/FaceLivenessDetection-Ionic-Cordova) |
| .NET MAUI | [FaceLivenessDetection-DotNet-MAUI](https://github.com/Faceplugin-ltd/FaceLivenessDetection-DotNet-MAUI) |
| Windows (server) | [FaceLivenessDetection-Windows](https://github.com/Faceplugin-ltd/FaceLivenessDetection-Windows) |
| **Linux / Docker** (server) | **[Docker Hub](https://hub.docker.com/r/faceplugin/face-liveness)** · **[FaceLivenessDetection-Docker](https://github.com/Faceplugin-ltd/FaceLivenessDetection-Docker)** **(this repo)** |

### Related products

Need **active liveness** — blink, smile, turn your head? That is an on-device feature; start with the mobile SDKs above, for example [FaceLivenessDetection-Android](https://github.com/Faceplugin-ltd/FaceLivenessDetection-Android) or [FaceLivenessDetection-iOS](https://github.com/Faceplugin-ltd/FaceLivenessDetection-iOS).

Face recognition, on-premise servers:

- **Docker** — [Docker Hub](https://hub.docker.com/r/faceplugin/face-recognition) · [FaceRecognition-Docker](https://github.com/Faceplugin-ltd/FaceRecognition-Docker)
- **Windows** — [FaceRecognition-Windows](https://github.com/Faceplugin-ltd/FaceRecognition-Windows)

On-device face recognition + liveness apps for mobile:

- **Android** — [FaceRecognition-LivenessDetection-Android](https://github.com/Faceplugin-ltd/FaceRecognition-LivenessDetection-Android)
- **iOS** — [FaceRecognition-LivenessDetection-iOS](https://github.com/Faceplugin-ltd/FaceRecognition-LivenessDetection-iOS)

## Before you start

| Step | What you need |
| ---- | ------------- |
| 1 | Docker Engine **on a Linux host**, **or** Linux x86_64 with glibc 2.38+ and Python 3.10+ |
| 2 | For a native run only: the runtime in `lib/cpu/` — see [Get the runtime](#get-the-runtime). The Docker image already contains it. |
| 3 | Start **without** a license, copy the machine code from the logs, send it to FacePlugin ([contact](#contact)), then activate with your license key |

You do **not** need a license to start the API. Product endpoints unlock after you activate.

### System requirements

| Item | Minimum | Recommended |
| ---- | ------- | ----------- |
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Disk | 4 GB | 8 GB |
| OS (Docker) | Linux + Docker Engine | Ubuntu 22.04 / 24.04 |
| OS (native) | Linux x86_64, glibc **2.38+** | Ubuntu 24.04 |
| Python (native) | 3.10+ | 3.12 |

Check your glibc with `ldd --version`. Debian Bookworm ships 2.36 and is **too old** for a native run — use Docker there.

## Get the runtime

**Docker users can skip this**: the runtime is already inside the image.

For a native run, `lib/cpu/` is empty on GitHub because the native libraries and model files are too large. This product is **CPU-only** — there is no `gpu/` package.

**[Download the runtime from Releases](https://github.com/Faceplugin-ltd/FaceLivenessDetection-Docker/releases/tag/latest)**

The release holds one archive, **`runtime.zip`** — there is a single runtime for this product.

1. Clone the repo (if you have not already):

```bash
git clone https://github.com/Faceplugin-ltd/FaceLivenessDetection-Docker.git
cd FaceLivenessDetection-Docker
```

2. Open the release page above and download **`runtime.zip`**.
3. Extract it and place the files **directly** in `lib/cpu/`, not in a subfolder.

```text
FaceLivenessDetection-Docker/
└── lib/
    └── cpu/
        ├── libFaceLivenessSDK.so
        ├── libfacerec.so
        ├── fal.fpk
        ├── libonnxruntime.so
        ├── libonnxruntime_providers_shared.so
        └── ... (remaining files from the archive)
```

> ⚠️ Move the extracted files up if the archive nests them, so you do not end up with `lib/cpu/SomeFolder/libFaceLivenessSDK.so`.

## Start the API

You do **not** need a license to start the API. The server prints your machine code on startup, which you need to [get a license](#how-to-get-a-license). Product endpoints unlock after you activate.

<p align="center">
 <img src="https://raw.githubusercontent.com/Faceplugin-ltd/faceplugin-assets/main/screenshots/face-liveness/desktop/unactivated.png" alt="Docker logs: machine code printed, activation failed, Flask API still listening" width="900"/>
</p>

### Option A — Docker

```bash
sudo docker pull faceplugin/face-liveness:latest

sudo docker run -d --name faceplugin-face-liveness \
  --shm-size=2gb --privileged \
  -p 8093:8093 \
  -v /etc/machine-id:/etc/machine-id:ro \
  faceplugin/face-liveness:latest

sudo docker logs -f faceplugin-face-liveness
# Look for the machine code line in the logs
```

**All three flags are mandatory.** `run.sh` checks them inside the container before it starts anything, and exits with an error if any is missing:

| Flag | What is checked |
| ---- | --------------- |
| `-v /etc/machine-id:/etc/machine-id:ro` | `/etc/machine-id` must be a mountpoint — otherwise the license binds to the container's own id, not the host's |
| `--shm-size=2gb` | `/dev/shm` must be at least ~1.9 GB |
| `--privileged` | `CAP_SYS_ADMIN` must be set in the container's effective capabilities |

So the image expects a **Linux host** — or a Linux VM — that can supply a real `/etc/machine-id`. On Docker Desktop for macOS or Windows there is no host `/etc/machine-id` to bind, and dropping the mount does not help: the container then fails the check and stops. Run it on a Linux host, or inside a Linux VM you control.

The repository also ships a [`docker-compose.yml`](docker-compose.yml) and a [`Dockerfile`](Dockerfile) if you prefer Compose or your own build. A local build needs `lib/cpu/` filled first — see [Get the runtime](#get-the-runtime).

**Several containers on one host:** to share one machine code and license across containers, see [the docs](https://doc.faceplugin.com/liveness-detection-sdk/server-sdk/liveness-detection-linux-sdk#run-multiple-containers).

### Option B — Native Linux (`./run.sh`)

```bash
pip3 install -r requirements.txt
./run.sh
```

API: **http://127.0.0.1:8093**. The machine code is printed in the terminal.

## SDK License

Licenses are **offline** and bound to your machine. Offline cryptography is pre-packaged within the SDK — no third-party licensing libraries or external OpenSSL installations are required.

### How to get a license

1. **Start the server** ([above](#start-the-api)). A license is not required for the first start.
2. **Copy the machine code** from the logs — it looks like **`FPMC1.…`** — or fetch it with `GET /api/machinecode`.
3. **Send that machine code** to FacePlugin ([contact](#contact)). We will issue a license key for that code.
4. **Activate** with the license key:

```bash
# Save the key, then post it
curl -s -X POST http://127.0.0.1:8093/api/activate \
  -H "Content-Type: text/plain" --data-binary @license.txt
```

Or mount it into the container, as [`docker-compose.yml`](docker-compose.yml) does:

```bash
-v $(pwd)/license.txt:/root/facesdk/license.txt
```

<p align="center">
 <img src="https://raw.githubusercontent.com/Faceplugin-ltd/faceplugin-assets/main/screenshots/face-liveness/desktop/activate.png" alt="POST /api/activate returning activated: true with the machine code" width="900"/>
</p>

The machine code comes from `/etc/machine-id`, which is why the host's file must be bound in read-only. Without that mount the code would follow the container and your license would stop matching after a recreate — so `run.sh` refuses to start at all. See [Option A — Docker](#option-a--docker).

### License capabilities

This product exposes **liveness** APIs only. A key labelled **Liveness only** or **Recognition + Liveness** unlocks `/api/liveness`; a **Recognition only** key leaves it unavailable here.

```bash
curl -s http://127.0.0.1:8093/api/licenseStatus
```

The Gradio demo shows the same summary as **License:** at the top of the page.

## Try it

### Health

```bash
curl -s http://127.0.0.1:8093/api/health
```

### Liveness

```bash
curl -s -X POST http://127.0.0.1:8093/api/liveness \
  -H "Content-Type: application/json" \
  -d '{"image":"<base64-jpeg>"}'

# or multipart, with the file in the `image` field (`file` is accepted too)
curl -s -X POST http://127.0.0.1:8093/api/liveness -F "image=@face.jpg"
```

The native JSON is passed through verbatim:

```json
{ "success": true, "code": 0, "message": "OK", "data": { "score": 0.72, "result": "Real", "pass": true } }
```

Common failures (`success: false`, `data: null`):

| `message` | Meaning |
| --------- | ------- |
| `NO_FACE` | No usable face in the image |
| `Image not suitable` | Missing or undecodable image |

Full protocol: [https://doc.faceplugin.com](https://doc.faceplugin.com).

### Security

This API has **no authentication**. By default it listens on **0.0.0.0** — every interface, which is what makes the published Docker port work — and answers browser requests from any origin.

| Variable | Purpose |
| -------- | ------- |
| `FACESDK_BIND_HOST` | Listen address. Default `0.0.0.0`. Set it to `127.0.0.1` for this machine only. |
| `PORT` / `FACESDK_PORT` | API port. Default `8093`. |
| `LICENSE` | A license key (`FP1.…`) or a path to a license file. Default `./license.txt`. |
| `FP_NO_LICENSE_PROMPT` | Set to `1` to skip the interactive paste prompt — for services and CI. |

Put it behind your own gateway, or publish the port only to a private network, before exposing it anywhere untrusted.

### Postman

Import [`postman/FaceLiveness-API.postman_collection.json`](postman/FaceLiveness-API.postman_collection.json). See [`postman/README.md`](postman/README.md) for the flow and failure messages.

Default base URL: `http://127.0.0.1:8093`. Routes are `/api/*` (`/api/check_liveness` aliases `/api/liveness`).

### Demo UI (Gradio) — local only

A local FacePlugin Face Liveness demo in the browser. The API must already be running on port 8093.

```bash
pip3 install -r requirements-demo.txt
DEMO_PORT=9093 API_BASE=http://127.0.0.1:8093 python3 demo.py
```

Open **http://127.0.0.1:9093**. Sample spoof images are in `assets/examples/samples/`.

Each run shows **Score**, **Result** (`Real` or `Spoof`) and **Pass**, with the raw JSON beside it.

<p align="center">
 <img src="https://raw.githubusercontent.com/Faceplugin-ltd/faceplugin-assets/main/screenshots/face-liveness/desktop/demo-ui.png" alt="FacePlugin Face Liveness demo — Real/Spoof result with score and Pass" width="900"/>
</p>

## Setup on your own app

Two ways to call the same engine. Full protocol: [https://doc.faceplugin.com](https://doc.faceplugin.com).

| Path | When to use |
| ---- | ----------- |
| **HTTP API** (Docker or `./run.sh`) | Any language. Keep the API running and `POST` a base64 JPEG to it. |
| **`sdk.py`** | Python on the **same** Linux machine as `lib/cpu/`. No HTTP hop. |

**HTTP (any language)**

1. Start the API and activate it once.
2. `POST /api/liveness` with `{"image":"<base64-jpeg>"}`.
3. Read `data.pass` for the verdict, and check `success` / `code` on every response.

**Python in-process**

1. Copy [`sdk.py`](sdk.py) and `lib/cpu/` into your project.
2. Put `lib/cpu` on `LD_LIBRARY_PATH` (that is all `run.sh` does).
3. Call `get_machine_code` → `activate` → `init_sdk`, then `liveness`.

The Gradio demo (`demo.py`) is a local test UI. You do not need it in production.

## About SDK

[`sdk.py`](sdk.py) is the Python binding. Every call returns `0` on success, or an error code.

**1. Get the machine code and request a license**

```python
import sdk

print(sdk.get_machine_code())   # FPMC1.…
```

**2. Activate, then initialize**

```python
ret = sdk.activate("license.txt")   # 0 on success
if ret == 0:
    ret = sdk.init_sdk()            # 0 on success

status = sdk.get_license_status()   # what the key unlocks
```

**3. Score a face**

```python
result = sdk.liveness(base64_image)   # JSON string
```

`data` is `{ "score": <float>, "result": "Real" | "Spoof", "pass": <bool> }`. Every RGB engine in the runtime is run and the scores are combined into that one verdict. Images arrive as base64 JPEG (a `data:` prefix is accepted); anything else is converted and re-encoded, and over 8 MB is downscaled.

HTTP endpoints: `/api/health`, `/api/machinecode`, `/api/licenseStatus`, `/api/backend`, `/api/activate`, `/api/liveness`, `/api/check_liveness`.

## Contact

<div align="left">
<a target="_blank" href="mailto:info@faceplugin.com"><img src="https://img.shields.io/badge/email-info@faceplugin.com-blue.svg?logo=gmail" alt="faceplugin.com"></a>&emsp;
<a target="_blank" href="https://t.me/FacePluginSupport"><img src="https://img.shields.io/badge/telegram-@FacePluginSupport-blue.svg?logo=telegram" alt="Telegram @FacePluginSupport"></a>&emsp;
<a target="_blank" href="https://wa.me/+14692784822"><img src="https://img.shields.io/badge/whatsapp-faceplugin-blue.svg?logo=whatsapp" alt="faceplugin.com"></a>
</div>
