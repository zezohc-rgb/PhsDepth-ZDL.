#!/usr/bin/env python3
"""Compare original and local patched TI binaries with an external Ziddle probe.
The emulator is NOT firmware/hardware certification. No pedal I/O occurs.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--probe',type=Path,required=True)
    p.add_argument('--report',type=Path,default=ROOT/'docs/filter-delay-boost/emulator-results.json')
    a=p.parse_args();cases=[];logs=[]
    original=ROOT/'original/FLTRDLY.ZDL';modified=ROOT/'build/FLTRDLY_BOOST.ZDL'
    with tempfile.TemporaryDirectory(prefix='fdb-emulator-') as work:
        work=Path(work);cache={}
        def render(path,db=0,controls='default',offset=0,engaged=True,skip_edits=False,scale=1,mode='stereo'):
            key=(str(path),db,controls,offset,engaged,skip_edits,scale,mode)
            if key in cache:return cache[key]
            output=work/f'{len(cache)}.f32'
            cmd=[str(a.probe),str(path),str(output),str(db),controls,str(offset),'on' if engaged else 'off',
                 'skip-edits' if skip_edits else 'edits',str(scale),mode]
            result=subprocess.run(cmd,capture_output=True,text=True,timeout=90)
            logs.append({'command':cmd,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
            if result.returncode:raise RuntimeError(result.stdout+result.stderr)
            if 'init_completed: true' not in result.stdout or 'init_unimplemented_hits: 0' not in result.stdout or 'unknown=0' not in result.stdout:
                raise RuntimeError('unclean emulation: '+result.stdout)
            raw=output.read_bytes();samples=struct.unpack('<'+str(len(raw)//4)+'f',raw)
            if len(samples)!=96000 or not all(map(math.isfinite,samples)):raise RuntimeError('invalid output')
            cache[key]=(raw,samples);return cache[key]
        def compare(label,db=0,controls='default',offset=0,engaged=True,skip_edits=False,scale=1,mode='stereo'):
            refraw,ref=render(original,0,controls,offset,engaged,skip_edits,scale,mode)
            raw,out=render(modified,db,controls,offset,engaged,skip_edits,scale,mode)
            gain=10**(db/20) if engaged else 1
            errors=[abs(y-x*gain) for x,y in zip(ref,out)]
            maxerr=max(errors)
            energy=sum(x*x for x in ref)
            measured=sum(x*y for x,y in zip(ref,out))/energy if energy else None
            case={'case':label,'boost_db':db,'engaged':engaged,'image_offset':offset,'startup_without_edit_pass':skip_edits,
                  'input_mode':mode,'controls':controls,'sample_values':len(ref),'max_abs_gain_error':maxerr,
                  'bit_exact':refraw==raw,'expected_gain':gain,'measured_gain':measured,
                  'reference_peak':max(map(abs,ref)),'output_peak':max(map(abs,out)),
                  'over_full_scale_samples':sum(abs(v)>1 for v in out)}
            if maxerr>2e-7*max(1,case['output_peak']):raise AssertionError(case)
            if gain==1 and not case['bit_exact']:raise AssertionError('unity/bypass not bit exact: '+label)
            if not energy:raise AssertionError('silent comparison: '+label)
            cases.append(case);print(label, 'PASS',f'error={maxerr:.3g}',flush=True)
        for db in range(13):compare(f'gain_{db}',db)
        for name,controls in [('dry','499,0,0,6,100,8,100,0'),('wet_tail','1,40,100,6,100,8,100,1'),('variant','123,65,55,30,60,2,80,1')]:
            for db in (0,12):compare(name+f'_{db}',db,controls)
        for tail in (0,1):compare(f'bypass_tail_{tail}',12,f'499,50,90,6,100,8,100,{tail}',engaged=False)
        compare('rebased_unity',0,offset=1048576)
        compare('rebased_boost',12,offset=1048576)
        for mode in ('left','right'):compare(mode+'_only',12,mode=mode)
        compare('edit_callback',12,skip_edits=False)
        compare('clipping_headroom',12,scale=10)
        assert cases[-1]['reference_peak']<1 and cases[-1]['over_full_scale_samples']>0
    report={'emulator':'Ziddle source ziddle-1793487371; synthetic host callbacks; no firmware image loaded',
            'source_url':'https://berbasoft.com/ziddle/ziddle-1793487371.zip',
            'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
            'modified_sha256':hashlib.sha256(modified.read_bytes()).hexdigest(),
            'tests_passed':len(cases),'renders':len(logs),'frames_per_render':48000,
            'audio_and_init_unknown_opcodes':0,'startup_coefficient_checked_before_edit_pass':True,
            'limitation':'Without a post-init edit pass, both original and candidate render silence in this synthetic host; complete firmware startup was not validated.','hardware_tested':False,'cases':cases,'runs':logs}
    a.report.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',len(cases),'comparisons;',len(logs),'renders')
if __name__=='__main__':main()
