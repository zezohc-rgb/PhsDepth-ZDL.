#!/usr/bin/env python3
"""Recheck current remote commits against full prior ID evidence, fail on changes."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
p=argparse.ArgumentParser();p.add_argument('previous_audit',type=Path);a=p.parse_args()
old=json.loads(a.previous_audit.read_text())
def check(r):
    req=urllib.request.Request('https://api.github.com/repos/'+r['repository']+'/commits/HEAD',headers={'User-Agent':'DmTrem-ID-audit'})
    with urllib.request.urlopen(req,timeout=30) as f:head=json.load(f)['sha']
    if head!=r['commit']:raise RuntimeError(f'{r["repository"]} changed: repeat full header audit')
    ids=sorted({tuple(v) for f in r['files'] for v in f['identities']})
    assert all(fx!=949 for gid,fx in ids),r['repository']
    return {'repository':r['repository'],'commit':head,'source_files':len(r['files']),'identities':[list(v) for v in ids]}
with ThreadPoolExecutor(max_workers=7) as ex:repos=list(ex.map(check,old['repositories']))
report={'candidate':{'gid':6,'fxid':949},'clear_in_audited_sources':True,'checked_at_utc':datetime.now(timezone.utc).isoformat(),'previous_full_audit_sha256':hashlib.sha256(a.previous_audit.read_bytes()).hexdigest(),'repositories':repos,'same_repository_effects':[{'effect':'PhaserZeh','gid':6,'fxid':947},{'effect':'CE2Soul','gid':6,'fxid':948}],'registry':'repeat98 docs/FXID-REGISTRY.md at 32f3d6877d892409c6defeeeec57040ad004d31f; no reservation covers 949 in gid6','limitations':'Bounded public snapshot, not a global reservation or inventory of the physical pedal.'}
out=Path(__file__).resolve().parents[1]/'docs/id-audit.json';out.write_text(json.dumps(report,indent=2)+'\n');print('MOD 949 clear in rechecked sources')
