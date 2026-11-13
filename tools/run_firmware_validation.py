#!/usr/bin/env python3
"""Run selected actual-firmware probes; retain unsupported full-loader evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
FW_SHA='4353e745b44ad61a1ccdc338166139d72ceb9b8e45cacf30384b58493dc7f6ed'
ORIGINAL_SHA='19ea42ed3b37783abfb4440a527e12a6f7ef92f31ed24d881bbb5eed09364c8e'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--body-probe',type=Path,required=True);p.add_argument('--init-probe',type=Path,required=True)
    p.add_argument('--ziddle',type=Path)
    p.add_argument('--firmware',type=Path,default=ROOT/'original/firmware/image-0.tipa')
    p.add_argument('--candidate',type=Path,default=ROOT/'build/FLTRDLY_BOOST.ZDL')
    a=p.parse_args();original=ROOT/'original/FLTRDLY.ZDL';docs=ROOT/'docs/filter-delay-boost'
    if sha(a.firmware)!=FW_SHA or sha(original)!=ORIGINAL_SHA:raise ValueError('firmware/original hash mismatch')
    paths=[docs/'firmware-body-results.json',docs/'firmware-init-results.json']
    commands=[[str(a.body_probe),str(a.firmware),str(a.candidate),str(paths[0])],
              [str(a.init_probe),str(a.firmware),str(original),str(a.candidate),str(paths[1])]]
    for cmd in commands:
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    body=json.loads(paths[0].read_text());init=json.loads(paths[1].read_text())
    if init['test_count']!=78 or init['diagnostics'] or not init['six_slots_same_image_isolation']['passed']:
        raise ValueError('firmware init evidence incomplete')
    if len(body['copy_tests'])!=16 or body['raw_lookup_tests']!=66:raise ValueError('firmware body evidence incomplete')
    report={'firmware_sha256':FW_SHA,'original_zdl_sha256':ORIGINAL_SHA,'candidate_sha256':sha(a.candidate),
            'actual_firmware_init_comparisons':78,'actual_firmware_copy_tests':16,'actual_firmware_raw_lookup_tests':66,
            'six_slot_isolation_passed':True,'coefficient_bytes_requested':192,
            'startup_reserved_bytes_per_slot':[r['reserved_bytes'] for r in init['coefficient_allocations']],
            'commands':commands,'full_loader_replayed':False,'full_firmware_boot_tested':False,
            'physical_hardware_tested':False,'modelled_preconditions':['mapped startup RAM','B14 as firmware startup specifies','B14[98]=1 as the firmware init dispatcher specifies']}
    if a.ziddle:
        cmd=[str(a.ziddle),'firmware','fit',str(a.firmware),str(a.candidate),'--json']
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
        report['loader_fit_command']=cmd;report['loader_fit_exit_code']=r.returncode
        report['loader_fit_result']=json.loads(r.stdout)
        # Lack of a recorded original-MS-70CDR profile is an honest blocker,
        # not proof of rejection by the firmware loader.
    (docs/'firmware-validation-summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['commands','loader_fit_result']},indent=2))
if __name__=='__main__':main()
