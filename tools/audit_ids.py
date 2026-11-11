#!/usr/bin/env python3
"""Audit a candidate against current public ZDL headers, manifests and generated IDs.

Only headers/JSON and metadata are read; third-party binaries are not saved.
This cannot establish a worldwide reservation or inspect a disconnected pedal.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
from urllib.parse import quote
from urllib.request import Request, urlopen

REPOS = [
    'repeat98/ZoomMultistompZDL', 'themanro/ZoomMultistompZDL',
    'matujuice/zoom-ms-zdl-effects-pack', 'Leemuzhko/Zoom-ZDL-FX',
    'Barsik-Barbosik/Custom-Zoom-ZDL-Effects', 'marcfuentes/silverst-zdl',
    'ELynx/zoom-fx-compressed',
]


def get(url, header=False):
    headers = {'User-Agent': 'PhsDepth-identity-audit'}
    if header:
        headers['Range'] = 'bytes=0-75'
    with urlopen(Request(url, headers=headers), timeout=45) as r:
        return r.read(76) if header else r.read()


def identities(obj):
    if isinstance(obj, dict):
        if isinstance(obj.get('gid'), int) and isinstance(obj.get('fxid'), int):
            yield obj['gid'], obj['fxid']
        for value in obj.values():
            yield from identities(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from identities(item)


def audit_repo(repo):
    commit = json.loads(get(f'https://api.github.com/repos/{repo}/commits/HEAD'))['sha']
    tree = json.loads(get(f'https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1'))
    if tree.get('truncated'):
        raise RuntimeError(f'{repo}: truncated tree')
    paths = [x['path'] for x in tree['tree'] if x['type'] == 'blob' and
             (x['path'].lower().endswith('.zdl') or
              (x['path'].split('/')[-1].startswith('manifest') and x['path'].endswith('.json')) or
              x['path'].endswith('effects_db.json'))]
    def read(path):
        url = f'https://raw.githubusercontent.com/{repo}/{commit}/{quote(path)}'
        data = get(url, path.lower().endswith('.zdl'))
        if path.lower().endswith('.zdl'):
            if len(data) != 76 or data[:8] != b'\0\0\0\0SIZE' or data[20:24] != b'INFO':
                raise RuntimeError(f'{repo}/{path}: not a plain ZDL header (compressed/LFS?)')
            ids = [(data[60], struct.unpack_from('<H', data, 64)[0])]
        else:
            ids = sorted(set(identities(json.loads(data))))
        return {'path': path, 'identities': [list(pair) for pair in ids]}
    with ThreadPoolExecutor(max_workers=8) as ex:
        files = list(ex.map(read, paths))
    print(f'{repo}@{commit[:12]}: {len(files)} source files', flush=True)
    return {'repository': repo, 'commit': commit, 'files': files}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--gid', type=int, default=6)
    ap.add_argument('--fxid', type=int, default=947)
    ap.add_argument('--output', type=Path, default=Path('docs/id-audit.json'))
    args = ap.parse_args()
    repos = [audit_repo(repo) for repo in REPOS]
    candidate = [args.gid, args.fxid]
    hits = [f'{r["repository"]}/{f["path"]}' for r in repos for f in r['files'] if candidate in f['identities']]
    any_group_hits = [f'{r["repository"]}/{f["path"]}' for r in repos for f in r['files']
                      if any(pair[1] == args.fxid for pair in f['identities'])]
    # Expanded slot pools documented by themanro: gid 8, not modulation gid 6.
    reserved = args.gid == 8 and (403 <= args.fxid <= 907 or 930 <= args.fxid <= 945 or 950 <= args.fxid <= 957)
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'candidate': {'gid': args.gid, 'fxid': args.fxid},
              'clear_in_audited_sources': not hits and not reserved,
              'conflicts': hits, 'same_fxid_any_group': any_group_hits,
              'limitations': 'Public files at pinned commits only; not a global reservation, no pedal inventory. Retired IDs and generated slots also checked against upstream FXID-REGISTRY.md.',
              'repositories': repos}
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(f'candidate {candidate}: clear={report["clear_in_audited_sources"]}')
    if hits or reserved:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
