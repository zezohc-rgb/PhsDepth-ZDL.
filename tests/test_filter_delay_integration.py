"""Binary invariants for a LOCAL candidate; skip when proprietary inputs absent."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from inspect_zdl import inspect
from zdl_elf import Elf

class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original=ROOT/'original/FLTRDLY.ZDL';modified=ROOT/'build/FLTRDLY_BOOST.ZDL'
        if not original.exists() or not modified.exists():raise unittest.SkipTest('local original/candidate unavailable')
        cls.raw=original.read_bytes();cls.new=modified.read_bytes()
        cls.before=inspect(cls.raw);cls.after=inspect(cls.new)
        cls.o=Elf(cls.raw[76:]);cls.n=Elf(cls.new[76:])
        cls.dyn=cls.n.symbols('.dynsym')

    def test_original_hash_locked(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),'19ea42ed3b37783abfb4440a527e12a6f7ef92f31ed24d881bbb5eed09364c8e')

    def test_stock_audio_bit_exact(self):
        self.assertEqual(self.o.section('.text')['data'][:0x820],self.n.section('.text')['data'][:0x820])

    def test_all_stock_instructions_unchanged_except_relocated_addresses(self):
        old=self.o.section('.text')['data'];new=self.n.section('.text')['data'][:len(old)]
        permitted=set()
        for addr,info,_ in self.o.relocations('.rela.dyn'):
            if addr<0x80000000:permitted.update(range(addr,addr+4))
        self.assertTrue(all(x==y or i in permitted for i,(x,y) in enumerate(zip(old,new))))

    def test_all_original_controls_preserved(self):
        old=self.before['descriptor'][2:];new=self.after['descriptor'][2:10]
        for a,b in zip(old,new):
            for key in ('name','max','default','pedal_max','handler','formatter'):
                self.assertEqual(a[key],b[key])
            self.assertEqual(b['flags'],a['flags']&~4)

    def test_ninth_control_boost(self):
        row=self.after['descriptor'][10]
        self.assertEqual((row['name'],row['max'],row['default'],row['flags'],row['handler']),('BOOST',12,0,4,'FDB_edit'))

    def test_audio_init_and_entry_routed_to_adapter(self):
        row=self.after['descriptor'][1]
        self.assertEqual((row['audio'],row['handler']),('FDB_audio','FDB_init'))
        dll=next(s for s in self.dyn if s['name']=='Dll_FltrDlyB')
        self.assertEqual(dll['words'][1],self.after['entry'])

    def test_original_graphic_and_three_visible_slots_preserved(self):
        a=self.o.section('.const')['data'];b=self.n.section('.const')['data']
        self.assertEqual(a[:620],b[:620])
        # UI only differs at three relocated KNOB_INFO pointers.
        allowed=set(range(0x480,0x484))|set(range(0x490,0x494))|set(range(0x4a0,0x4a4))
        self.assertTrue(all(a[i]==b[i] or i in allowed for i in range(0x450,0x524)))
        self.assertEqual(self.after['ui_field_at_0x20'],3)

    def test_extended_coefficients_preserve_stock_defaults(self):
        s=next(s for s in self.dyn if s['name']=='FDB_Coe')['words'];off=s[1]-0x80000000
        raw=self.n.section('.const')['data']
        self.assertEqual(s[2],192)
        self.assertEqual(raw[off:off+188],self.o.section('.const')['data'][0x524:0x5e0])
        self.assertEqual(struct.unpack_from('<f',raw,off+188)[0],1)

    def test_gain_table_all_13_values(self):
        s=next(s for s in self.dyn if s['name']=='fdb_gains')['words']
        gains=struct.unpack_from('<13f',self.n.section('.const')['data'],s[1]-0x80000000)
        for db,g in enumerate(gains):self.assertAlmostEqual(g/(10**(db/20)),1,places=6)

    def test_header_identity_separate_from_original(self):
        self.assertEqual(self.after['gid'],8)
        self.assertNotEqual(self.after['fxid'],self.before['fxid'])
        self.assertEqual(self.after['fxid'],65534) # emulator-only candidate, not reserved for hardware.

    def test_memory_and_size_envelope(self):
        self.assertLessEqual(len(self.new),32126)
        const=self.n.section('.const')['words'];far=self.n.section('.fardata')['words']
        self.assertGreaterEqual(far[3],const[3]+const[5])
        self.assertEqual(self.o.section('.fardata')['data'],self.n.section('.fardata')['data'])
        self.assertEqual(far[5],24)
        self.assertEqual(self.after['descriptor'][1]['cost'],40.0)

    def test_dynamic_tags_match_rebuilt_file_offsets(self):
        tags=dict(struct.unpack_from('<II',self.n.section('.dynamic')['data'],i) for i in range(0,len(self.n.section('.dynamic')['data']),8))
        for tag,name in [(4,'.hash'),(5,'.dynstr'),(6,'.dynsym'),(7,'.rela.dyn')]:
            self.assertEqual(tags[tag],self.n.section(name)['words'][4])
        self.assertEqual(tags[8],len(self.n.section('.rela.dyn')['data']))
        self.assertEqual(tags[10],len(self.n.section('.dynstr')['data']))
        self.assertEqual(tags[0x6000000d],next(i for i,s in enumerate(self.dyn) if s['name']=='Dll_FltrDlyB')*16)

    def test_all_absolute_relocations_have_matching_initial_contents(self):
        rels=self.n.relocations('.rela.dyn');self.assertEqual(len(rels),65)
        for addr,info,addend in rels:
            target=self.dyn[info>>8]['words'][1]+addend;kind=info&255
            sec=self.n.section('.text' if addr<0x80000000 else '.const')
            w=struct.unpack_from('<I',sec['data'],addr-sec['words'][3])[0]
            if kind==1:self.assertEqual(w,target)
            elif kind==9:self.assertEqual((w>>7)&65535,target&65535)
            elif kind==10:self.assertEqual((w>>7)&65535,target>>16)
            else:self.fail('unexpected relocation')

    def test_dynamic_hash_chains_reach_every_named_symbol(self):
        raw=self.n.section('.hash')['data'];nb,nc=struct.unpack_from('<II',raw)
        self.assertEqual(nc,len(self.dyn));buckets=struct.unpack_from('<'+str(nb)+'I',raw,8);chains=struct.unpack_from('<'+str(nc)+'I',raw,8+4*nb)
        seen=set()
        for b in buckets:
            walked=set()
            while b:
                self.assertNotIn(b,walked);self.assertLess(b,nc);walked.add(b);seen.add(b);b=chains[b]
        self.assertEqual(seen,set(range(1,nc)))

    def test_official_linker_resolved_original_function_calls(self):
        obj=Elf((ROOT/'build/zoom_adapter.obj').read_bytes());syms=obj.symbols()
        base=len(self.o.section('.text')['data']);newtext=self.n.section('.text')['data']
        originalsyms={s['name']:s['words'][1] for s in self.o.symbols()}
        rel=obj.section('.rel.text')['data'];count=0
        for off in range(0,len(rel),8):
            pos,info=struct.unpack_from('<II',rel,off);self.assertEqual(info&255,4)
            target=originalsyms[syms[info>>8]['name']]
            word=struct.unpack_from('<I',newtext,base+pos)[0];disp=(word>>7)&0x1fffff
            if disp&(1<<20):disp-=1<<21
            self.assertEqual(((base+pos)&~31)+4*disp,target);count+=1
        self.assertEqual(count,8)

if __name__=='__main__':unittest.main()
