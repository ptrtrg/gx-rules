# geosite builder

Builds a merged `geosite.dat` for V2Ray/Xray/sing-box routing clients.

It takes the upstream [`runetfreedom/russia-v2ray-rules-dat`](https://github.com/runetfreedom/russia-v2ray-rules-dat)
`geosite.dat` as a base (so all its categories — `ru-blocked`, `youtube`,
`telegram`, `openai`, … — keep working and stay fresh) and appends one custom
category, **`ai-extra`**, built from [`domains.txt`](domains.txt): AI/LLM service
domains that the upstream lists don't cover.

The result is a single `geosite.dat` that a routing profile can reference as
both upstream categories (`geosite:ru-blocked`) and the custom one
(`geosite:ai-extra`) from one `GeositeUrl`.

## Output

A GitHub Action rebuilds on every push to `domains.txt` and every 6 hours, then
force-pushes the result to the `release` branch:

```
https://raw.githubusercontent.com/<owner>/<repo>/release/geosite.dat
```

Point your client's `GeositeUrl` at that URL. Clients refresh geo-files on their
own schedule, so edits propagate without re-importing the routing profile.

## Add / remove a domain

Edit [`domains.txt`](domains.txt) (one domain per line; `#` comments allowed)
and push to `main`. Each entry is a root-domain match — `groq.com` covers
`api.groq.com`, `console.groq.com`, etc. The Action does the rest.

## Build locally

```bash
pip install -r requirements.txt
python -m grpc_tools.protoc -Iproto --python_out=. proto/geosite.proto
python build.py --out geosite.dat
```
