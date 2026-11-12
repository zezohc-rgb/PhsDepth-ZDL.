#!/usr/bin/env python3
import argparse,ctypes as C,hashlib,json,pathlib,re,shutil,struct,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--ziddle',type=pathlib.Path,required=True);a=p.parse_args();z=a.ziddle.resolve()
w=ROOT/'work/emulator';(w/'src').mkdir(parents=True,exist_ok=True)
shutil.copy2(pathlib.Path(__file__).with_name('main.rs'),w/'src/main.rs');shutil.copy2(pathlib.Path(__file__).with_name('Cargo.lock'),w/'Cargo.lock')
(w/'Cargo.toml').write_text('[package]\nname="ce2-binary-test"\nversion="0.1.0"\nedition="2021"\n[workspace]\n[dependencies]\n'+f'ziddle-effect-emulator={{path="{z}/ziddle/runtime/effect-emulator"}}\nziddle-effect-runtime={{path="{z}/ziddle/runtime/effect-runtime"}}\n')
subprocess.run(['cc','-O2','-ffp-contract=off','-shared','-fPIC',str(ROOT/'src/ce2_dsp.c'),'-o',str(w/'host.so')],check=True)
l=C.CDLL(str(w/'host.so'));l.ce2_state_size.restype=C.c_size_t;l.ce2_init.argtypes=[C.c_void_p,C.c_float,C.c_float];l.ce2_process.argtypes=[C.c_void_p,C.c_void_p,C.c_void_p,C.c_uint,C.c_float,C.c_float]
cases=[(r,d) for r in (0,50,100) for d in (0,50,100)];v=bytearray(struct.pack('<I',len(cases)));rng=12345
for rate,depth in cases:
 blocks=16384 if rate==50 and depth==50 else 4096
 v.extend(struct.pack('<2fI',rate,depth,blocks));s=C.create_string_buffer(l.ce2_state_size());l.ce2_init(s,rate/100,depth/100)
 for block in range(blocks):
  rr,dd=(rate,depth) if block<blocks//2 else (100-rate,100-depth)
  inp=(C.c_float*8)();out=(C.c_float*8)()
  for i in range(8):
   rng=(1664525*rng+1013904223)&0xffffffff
   inp[i]=((rng>>16)-32768)/131072 if block<blocks*3//4 else 0
  l.ce2_process(s,inp,out,8,rr/100,dd/100)
  # R deliberately differs; enabled effect must use only L and duplicate mono.
  v.extend(struct.pack('<32f',*inp,*[-x*.5 for x in inp],*out,*out))
(w/'vectors.bin').write_bytes(v)
subprocess.run(['cargo','build','--locked','--release','--manifest-path',str(w/'Cargo.toml')],check=True)
r=subprocess.run([str(w/'target/release/ce2-binary-test'),str(ROOT/'build/CE2Soul.ZDL'),str(w/'vectors.bin')],capture_output=True,text=True)
log=r.stdout+r.stderr;print(log);(w/'result.txt').write_text(log)
m=re.search(r'PASS: (\d+) cases, (\d+) samples, max error ([\d.]+), max packets (\d+), emulator cycles (\d+), unsupported 0',log)
report={'passed':r.returncode==0,'artifact_sha256':hashlib.sha256((ROOT/'build/CE2Soul.ZDL').read_bytes()).hexdigest(),'physical_hardware_test':False,'scope':'C674x execution with hermetic callbacks; not firmware loader, ADC, CPU scheduling or CE-2 sound validation','ziddle_source':'https://berbasoft.com/ziddle/ziddle-1793487371.zip','ziddle_zip_sha256':'c45f11a0ffa51c327169c3c8c6965043882d39b4a8f5f0ac624603e5941579a3','metrics':None if not m else {'cases':int(m[1]),'samples':int(m[2]),'max_abs_error':float(m[3]),'max_packets':int(m[4]),'max_emulated_cycles':int(m[5]),'unsupported_instructions':0},'log':log}
(ROOT/'build/emulator-report.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(r.returncode)
