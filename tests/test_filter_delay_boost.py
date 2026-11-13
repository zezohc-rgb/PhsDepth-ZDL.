"""Host tests only. No original DSP emulation or hardware claims."""
import ctypes as C
import hashlib
import importlib.util
import math
from pathlib import Path
import random
import struct
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]

def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/f'{name}.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class GainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(['python',str(ROOT/'tools/build_filter_delay_boost.py')],check=True,stdout=subprocess.DEVNULL)
        cls.lib=C.CDLL(str(ROOT/'build/filter_delay_boost.so'))
        cls.lib.fdb_process.argtypes=[C.POINTER(C.c_float),C.POINTER(C.c_float),C.c_size_t,C.c_uint]
        cls.lib.fdb_process.restype=C.c_int
        cls.lib.fdb_gain.argtypes=[C.c_uint];cls.lib.fdb_gain.restype=C.c_float

    def test_all_gains_and_db(self):
        for db in range(13):
            gain=self.lib.fdb_gain(db)
            self.assertAlmostEqual(gain/10**(db/20),1,places=6)
            self.assertAlmostEqual(20*math.log10(gain),db,places=5)

    def test_unity_bit_exact(self):
        # Include signed zero, subnormals, infinities, quiet/signaling NaN payloads.
        bits=[0,0x80000000,1,0x80000001,0x7f800000,0xff800000,0x7fc12345,0x7f812345,0x3f800000]
        for db in [0]:
            a=(C.c_uint32*len(bits))(*bits); before=bytes(a)
            self.assertEqual(self.lib.fdb_process(C.cast(a,C.POINTER(C.c_float)),None,len(bits),db),0)
            self.assertEqual(bytes(a),before)

    def test_stereo_independent_no_crosstalk(self):
        rng=random.Random(70)
        ls=[rng.uniform(-.2,.2) for _ in range(257)]
        rs=[rng.uniform(-.2,.2) for _ in range(257)]
        for db in range(13):
            l=(C.c_float*len(ls))(*ls);r=(C.c_float*len(rs))(*rs)
            before_l=list(l);before_r=list(r)
            self.assertEqual(self.lib.fdb_process(l,r,len(ls),db),0)
            for b,a in zip(before_l,l): self.assertAlmostEqual(a,b*10**(db/20),places=6)
            for b,a in zip(before_r,r): self.assertAlmostEqual(a,b*10**(db/20),places=6)

    def test_zero_right_remains_zero(self):
        l=(C.c_float*8)(*[.1]*8);r=(C.c_float*8)()
        self.lib.fdb_process(l,r,8,12)
        self.assertTrue(all(x==0 for x in r))

    def test_no_hidden_limiter_and_headroom(self):
        for db in range(1,13):
            gain=10**(db/20);threshold=1/gain
            a=(C.c_float*2)(threshold*.99,threshold*1.01)
            self.lib.fdb_process(a,None,2,db)
            self.assertLess(a[0],1);self.assertGreater(a[1],1)
        self.assertAlmostEqual(1/10**(.6),.251188643150958,places=12)

    def test_invalid_controls_no_mutation(self):
        a=(C.c_float*2)(.1,-.2);before=bytes(a)
        for db in [13,100,2**32-1]:
            self.assertEqual(self.lib.fdb_process(a,None,2,db),-1)
            self.assertEqual(bytes(a),before)
        self.assertEqual(self.lib.fdb_process(a,a,2,1),-1)
        self.assertEqual(self.lib.fdb_process(None,None,2,1),-1)
        self.assertEqual(bytes(a),before)

    def test_empty_block(self):
        self.assertEqual(self.lib.fdb_process(None,None,0,12),0)

    def test_bounds_canaries(self):
        a=(C.c_float*4)(123,.1,-.2,456)
        p=C.cast(C.byref(a,4),C.POINTER(C.c_float))
        self.lib.fdb_process(p,None,2,12)
        self.assertEqual(a[0],123);self.assertEqual(a[3],456)

    def test_post_mix_linearity(self):
        # Mathematical placement test, synthetic dry/wet; not original DSP.
        dry=[.1,-.02,.03]; wet=[.03,.04,-.05]; mix=.6
        out=[d*(1-mix)+w*mix for d,w in zip(dry,wet)]
        a=(C.c_float*3)(*out);self.lib.fdb_process(a,None,3,9)
        for x,d,w in zip(a,dry,wet):
            self.assertAlmostEqual(x,(d*(1-mix)+w*mix)*10**(.45),places=6)

class OriginalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=ROOT/'original/FLTRDLY.ZDL'
        if not cls.p.exists(): raise unittest.SkipTest('official original not extracted locally')
        cls.data=cls.p.read_bytes();cls.inspector=module('inspect_zdl')

    def test_original_identity_structure_and_controls(self):
        r=self.inspector.inspect(self.data)
        self.assertEqual(r['sha256'],'19ea42ed3b37783abfb4440a527e12a6f7ef92f31ed24d881bbb5eed09364c8e')
        self.assertEqual((r['gid'],r['fxid'],r['elf_offset'],r['entry']),(8,112,76,0xfac))
        self.assertEqual([x['name'] for x in r['descriptor'][2:]],['Time','F.B','Mix','Rate','Depth','Reso','Level','Tail'])
        self.assertEqual(len(r['dynamic_relocations']),40)
        self.assertEqual(r['ui_field_at_0x20'],3) # It is NOT the total parameter count.

    def test_reject_truncation_and_trailing_bytes(self):
        for b in [self.data[:40],self.data[:-1],self.data+b'\0']:
            with self.assertRaises(ValueError):self.inspector.inspect(b)

    def test_reject_machine_mismatch(self):
        b=bytearray(self.data);struct.pack_into('<H',b,76+18,62)
        with self.assertRaises(ValueError):self.inspector.inspect(b)

    def test_reject_section_table_outside_file(self):
        b=bytearray(self.data);struct.pack_into('<I',b,76+32,0xfffffff0)
        with self.assertRaises(ValueError):self.inspector.inspect(b)

    def test_reject_missing_descriptor_sentinel(self):
        b=bytearray(self.data);offset=76+0x12e0+0x270+9*48+44
        struct.pack_into('<I',b,offset,0)
        with self.assertRaises((ValueError,UnicodeDecodeError)):self.inspector.inspect(b)

class ExtractionTests(unittest.TestCase):
    def fixture(self):
        d=bytearray(b'\xff'*(14*4096));d[:6]=bytes.fromhex('55aa00010400');struct.pack_into('<H',d,8,14)
        t=3*4096;d[t:t+8]=bytes.fromhex('01a50102ffffffff')
        effect=b'\0\0\0\0SIZE'+bytes(12)
        d[t+8:t+40]=struct.pack('<H2sI12s12s',1,b'\x01\xff',len(effect),b'FLTRDLY.ZDL\0',b'\xff'*12)
        struct.pack_into('<HHH',d,11*4096,0xffff,0xffff,len(effect));d[11*4096+6:11*4096+6+len(effect)]=effect
        return d,effect

    def test_linked_extraction(self):
        d,e=self.fixture();self.assertEqual(module('extract_filter_delay').extract(d)[0],e)

    def test_cycle_size_and_previous_rejected(self):
        for offset,value in [(11*4096,3),(11*4096+2,1),(11*4096+4,4091)]:
            d,_=self.fixture();struct.pack_into('<H',d,offset,value)
            with self.assertRaises(ValueError): module('extract_filter_delay').extract(d)

    def test_missing_or_duplicate_signature(self):
        for d in [b'bad',bytes.fromhex('55aa0001040055aa00010400')]:
            with self.assertRaises(ValueError): module('extract_filter_delay').extract(d)

if __name__=='__main__':unittest.main()
