#!/usr/bin/env python3
"""Build a merged geosite.dat.

Takes the upstream runetfreedom geosite.dat as a base (so all of its
categories — ru-blocked, youtube, telegram, openai, etc. — keep working and
auto-updating) and appends/replaces a single custom category built from
domains.txt. The result is a drop-in geosite.dat that a routing client can
reference as both `geosite:ru-blocked` (upstream) and `geosite:ai-extra` (ours)
from one GeositeUrl.

Usage:
    python3 build.py [--out geosite.dat] [--category AI-EXTRA] [--domains domains.txt]
"""
import argparse
import sys
import urllib.request

import geosite_pb2  # generated from proto/geosite.proto

UPSTREAM_GEOSITE = (
    "https://raw.githubusercontent.com/runetfreedom/"
    "russia-v2ray-rules-dat/release/geosite.dat"
)


def load_domains(path):
    domains = []
    seen = set()
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.split("#", 1)[0].strip().lower()
            if not line:
                continue
            if line in seen:
                continue
            seen.add(line)
            domains.append(line)
    return domains


def fetch_upstream(url):
    print(f"-> fetching upstream geosite.dat: {url}", file=sys.stderr)
    req = urllib.request.Request(url, headers={"User-Agent": "geosite-builder/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="geosite.dat")
    ap.add_argument("--category", default="AI-EXTRA",
                    help="custom category code (referenced lowercased as geosite:<code>)")
    ap.add_argument("--domains", default="domains.txt")
    ap.add_argument("--upstream", default=UPSTREAM_GEOSITE)
    args = ap.parse_args()

    code = args.category.upper()

    geolist = geosite_pb2.GeoSiteList()
    geolist.ParseFromString(fetch_upstream(args.upstream))
    upstream_count = len(geolist.entry)
    print(f"-> upstream categories: {upstream_count}", file=sys.stderr)

    # Drop any pre-existing entry with our code so re-runs are idempotent.
    kept = [e for e in geolist.entry if e.country_code.upper() != code]
    removed = upstream_count - len(kept)
    if removed:
        print(f"-> replaced existing '{code}' category", file=sys.stderr)

    domains = load_domains(args.domains)
    if not domains:
        sys.exit("no domains loaded — refusing to write empty category")

    site = geosite_pb2.GeoSite(country_code=code)
    for d in domains:
        site.domain.add(type=geosite_pb2.Domain.RootDomain, value=d)

    out = geosite_pb2.GeoSiteList()
    out.entry.extend(kept)
    out.entry.append(site)

    blob = out.SerializeToString()
    with open(args.out, "wb") as fh:
        fh.write(blob)

    print(
        f"OK: wrote {args.out} — {len(out.entry)} categories "
        f"({upstream_count} upstream + 1 custom '{code}' with "
        f"{len(domains)} domains), {len(blob)} bytes",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
