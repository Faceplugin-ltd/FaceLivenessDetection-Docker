Import `FaceLiveness-API.postman_collection.json`.

baseUrl: `http://127.0.0.1:8093`

Flow: Health → Machine code → License status → Activate (FP1.) → Liveness.

`POST /api/liveness` body: `{ "image": "<base64>" }`  
`POST /api/check_liveness` is the same route under another name.

Success `data`: `{ "score": <float>, "result": "Real" | "Spoof", "pass": <bool> }`

Score ≥ 0.5 is Real (`pass: true`). Below 0.5 is Spoof (`pass: false`).

Common failures (`data` is `null`):

| `message` | Meaning |
| --------- | ------- |
| `NO_FACE` | No usable face in the image |
| `Image not suitable` | Missing or undecodable image |
