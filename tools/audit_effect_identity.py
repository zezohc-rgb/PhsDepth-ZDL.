#!/usr/bin/env python3
"""Read-only ID audit against a pinned research checkout and optional pedal dump.
Absence from public lists is NOT global reservation or a hardware guarantee.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess


def add_ids(evidence,gid,ids,source):
    for fxid in ids:evidence.setdefault((gid,fxid),set()).add(source)


def registry_ids(text):
    rows=[];part=text.split('## IDs used by other collections',1)[-1]
    for line in part.splitlines():
        cells=[c.strip() for c in line.split('|')[1:-1]]
        if len(cells)<2 or not cells[0].isdigit():continue
        gid=int(cells[0]);values=[]
        for item in cells[1].replace('–','-').split(','):
            if re.fullmatch(r'\s*\d+\s*',item):
                value=int(item)
                if not 0<=value<=65535:raise ValueError('invalid scalar ID')
                values.append(value)
            elif re.fullmatch(r'\s*\d+\s*-\s*\d+\s*',item):
                lo,hi=map(int,item.split('-'))
                if not 0<=lo<=hi<=65535:raise ValueError('invalid registry range')
                values.extend(range(lo,hi+1))
            else:raise ValueError('unsupported registry cell '+cells[1])
        rows.append((gid,values))
    return rows


def scan_json(obj,evidence,source):
    if isinstance(obj,list):
        for value in obj:scan_json(value,evidence,source)
    elif isinstance(obj,dict):
        if isinstance(obj.get('gid'),int) and isinstance(obj.get('fxid'),int) and obj['fxid']>0:
            add_ids(evidence,obj['gid'],[obj['fxid']],source)
        for value in obj.values():scan_json(value,evidence,source)


def read_header(path):
    b=path.read_bytes()
    if len(b)<76 or b[:8]!=b'\0\0\0\0SIZE':raise ValueError('invalid ZDL header: '+str(path))
    return b[60],struct.unpack_from('<H',b,64)[0]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--research-root',type=Path,required=True)
    p.add_argument('--pedal-inventory',type=Path);p.add_argument('--candidate',type=Path)
    p.add_argument('--output',type=Path,default=Path('docs/filter-delay-boost/identity-audit.json'))
    a=p.parse_args();root=a.research_root;evidence={};sources=[]
    for path in [root/'docs/FXID-REGISTRY.md',root/'tools/effects_db.json']:
        sources.append({'file':str(path.relative_to(root)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    for gid,values in registry_ids((root/'docs/FXID-REGISTRY.md').read_text()):add_ids(evidence,gid,values,'upstream cross-collection registry')
    db=json.loads((root/'tools/effects_db.json').read_text());scan_json(db,evidence,'upstream effect database including legacy/probes')
    for group in db.get('generated',{}).values():
        if not all(isinstance(group.get(k),int) for k in ('first','last','fxidOffset')):raise ValueError('unknown generated ID range')
        add_ids(evidence,8,range(group['first']+group['fxidOffset'],group['last']+group['fxidOffset']+1),'generated NAM/CabIR slots')
    for path in sorted((root/'src').rglob('manifest*.json')):
        scan_json(json.loads(path.read_text()),evidence,'upstream source manifests')
    inventory=[]
    if a.pedal_inventory:
        files=sorted(p for p in a.pedal_inventory.rglob('*') if p.suffix.upper()=='.ZDL')
        if not files:raise ValueError('provided inventory contains no ZDLs')
        for path in files:
            gid,fxid=read_header(path);inventory.append({'name':path.name,'gid':gid,'fxid':fxid})
            add_ids(evidence,gid,[fxid],'provided local pedal inventory')
    candidate=None
    if a.candidate:
        gid,fxid=read_header(a.candidate)
        candidate={'file':a.candidate.name,'gid':gid,'fxid':fxid,'known_conflicts':sorted(evidence.get((gid,fxid),[])),
                   'within_common_custom_range_400_999':400<=fxid<=999}
    free=[fxid for fxid in range(958,1000) if all(fxid!=used for _,used in evidence)]
    report={'research_commit':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),
            'sources':sources,'occupied_gid_fxid_pairs':len(evidence),'candidate':candidate,
            'suggestions_without_known_use_in_any_gid':free,'pedal_inventory_supplied':a.pedal_inventory is not None,
            'pedal_inventory':inventory,'global_reservation_claimed':False,'hardware_compatibility_claimed':False,
            'limitation':'Pinned public catalogue only; verify current collections and the user pedal inventory before choosing a release ID.'}
    a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    if candidate and candidate['known_conflicts']:p.exit(1,'candidate conflicts with known effect\n')
if __name__=='__main__':main()
