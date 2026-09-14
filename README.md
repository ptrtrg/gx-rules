# gx-rules

`geosite.dat` builder. Merges an upstream `geosite.dat` with a custom category
defined in [`domains.txt`](domains.txt) and publishes the result to the
`release` branch:

```
https://raw.githubusercontent.com/ptrtrg/gx-rules/release/geosite.dat
```

Two oversized upstream categories (`ru-blocked-all`, `antifilter-download`,
~64 MB together) are dropped — nothing of ours references them, and the full
74 MB file made Happ time out on a cold CDN fetch. Pass `--keep-all` to keep
them. CI fails the build if the result exceeds 20 MB.

## Edit

Add or remove a line in [`domains.txt`](domains.txt) and push to `main`. Each
entry is a root-domain match (covers subdomains). CI rebuilds automatically.

## Build locally

```bash
pip install -r requirements.txt
python -m grpc_tools.protoc -Iproto --python_out=. proto/geosite.proto
python build.py --out geosite.dat
```
