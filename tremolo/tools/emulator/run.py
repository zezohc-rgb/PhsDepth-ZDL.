#!/usr/bin/env python3
import argparse,ctypes as C,hashlib,json,pathlib,re,shutil,struct,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--ziddle',type=pathlib.Path,required=True);a=p.parse_args();z=a.ziddle.resolve()
w=ROOT/'work/emulator';(w/'src').mkdir(parents=True,exist_ok=True)
shutil.copy2(pathlib.Path(__file__).with_name('main.rs'),w/'src/main.rs');shutil.copy2(pathlib.Path(__file__).with_name('Cargo.lock'),w/'Cargo.lock')
(w/'Cargo.toml').write_text('[package]\nname="dmtrem-binary-test"\nversion="0.1.0"\nedition="2021"\n[workspace]\n[dependencies]\n'+f'ziddle-effect-emulator={{path="{z}/ziddle/runtime/effect-emulator"}}\nziddle-effect-runtime={{path="{z}/ziddle/runtime/effect-runtime"}}\n')
subprocess.run(['cc','-std=c99','-O2','-ffp-contract=off','-shared','-fPIC',str(ROOT/'tools/emulator/host.c'),'-o',str(w/'host.so')],check=True)
l=C.CDLL(str(w/'host.so'));l.dm_host_size.restype=C.c_size_t
l.dm_host_set_bpm.argtypes=[C.c_uint];l.dm_host_reset.argtypes=[C.c_void_p];l.dm_host_block.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_void_p]
cases=[(40,75,50,wave,mode,float(mode%2),1,0) for wave in range(4) for mode in range(6)]
cases += [(speed,depth,volume,wave,0,0,0,0) for speed in (0,100) for depth in (0,100) for volume in (0,100) for wave in range(4)]
cases += [(40,75,50,wave,mode,float(mode%2),1,1) for wave in range(4) for mode in range(6)]
v=bytearray(struct.pack('<I',len(cases)));rng=12345
for knobs in cases:
 blocks=16384 if knobs[:3]==(0,100,100) else (4096 if knobs[0]==40 else 1024)
 v.extend(struct.pack('<8fI',*knobs,blocks));state=C.create_string_buffer(l.dm_host_size());l.dm_host_reset(state)
 changed=[100-knobs[0],100-knobs[1],100-knobs[2],3-knobs[3],5-knobs[4],1-knobs[5],1-knobs[6],1-knobs[7]]
 for block in range(blocks):
  ui=(C.c_float*8)(*(knobs if block<blocks//2 else changed))
  bpm=100 if block<blocks//4 else (60 if block<blocks*3//4 else 180)
  l.dm_host_set_bpm(bpm)
  v.extend(struct.pack('<I',bpm))
  inp=(C.c_float*16)();out=(C.c_float*16)()
  for i in range(8):
   rng=(1664525*rng+1013904223)&0xffffffff
   inp[i]=((rng>>16)-32768)/131072 if block<blocks*3//4 else 0
   inp[i+8]=-inp[i]*.5
  l.dm_host_block(state,ui,inp,out)
  v.extend(struct.pack('<32f',*inp,*out))
(w/'vectors.bin').write_bytes(v)
subprocess.run(['cargo','build','--locked','--release','--manifest-path',str(w/'Cargo.toml')],check=True)
r=subprocess.run([str(w/'target/release/dmtrem-binary-test'),str(ROOT/'build/DmTrem.ZDL'),str(w/'vectors.bin')],capture_output=True,text=True)
log=r.stdout+r.stderr;print(log);(w/'result.txt').write_text(log)
m=re.search(r'PASS: (\d+) cases, (\d+) samples, max error ([\d.]+), max packets (\d+), emulator cycles (\d+), unsupported 0',log)
report={'passed':r.returncode==0,'artifact_sha256':hashlib.sha256((ROOT/'build/DmTrem.ZDL').read_bytes()).hexdigest(),'physical_hardware_test':False,'scope':'C674x execution with hermetic callbacks; not firmware loader, ADC, CPU scheduling or Diamond sound validation','ziddle_source':'https://berbasoft.com/ziddle/ziddle-1793487371.zip','ziddle_zip_sha256':'c45f11a0ffa51c327169c3c8c6965043882d39b4a8f5f0ac624603e5941579a3','metrics':None if not m else {'cases':int(m[1]),'samples':int(m[2]),'max_abs_error':float(m[3]),'max_packets':int(m[4]),'max_emulated_cycles':int(m[5]),'unsupported_instructions':0},'host_tempo_changes_bpm':[100,60,180],'tap_service':'STATE[24](quarter=6, ceiling=8000), captured by Tap_edit','physical_tap_test_pending':True,'independent_tap_period_oracle_passed':r.returncode==0 and 'PASS TAP:' in log,'log':log}
(ROOT/'build/emulator-report.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(r.returncode)
