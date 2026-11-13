"""Bounds/identity regressions for read-only research tools; no firmware fixtures."""
import importlib.util
from pathlib import Path
import struct
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from extract_firmware_research import parse_tipa,wrap_code_elf
from audit_effect_identity import registry_ids,scan_json,read_header
from zdl_elf import Elf

class TipaTests(unittest.TestCase):
    def image(self,address=0x1000,size=16,entry=0x1000):
        return b'TIPA'+bytes(12)+b'\x01YSX'+struct.pack('<II',address,size)+bytes(size)+b'\x06YSX'+struct.pack('<I',entry)

    def test_valid_record_addresses_and_bounds(self):
        data=self.image();r=parse_tipa(data,0)
        self.assertEqual(r['entry'],0x1000);self.assertEqual(r['tipa_end'],len(data))
        self.assertEqual(r['segments'],[{'address':0x1000,'size':16,'file_offset':28}])

    def test_reject_truncated_record_and_missing_entry(self):
        data=self.image()
        for truncated in (data[:25],data[:-1],data[:-8]):
            with self.assertRaises(ValueError):parse_tipa(truncated,0)

    def test_reject_zero_length_and_entry_outside_segments(self):
        for data in (self.image(size=0),self.image(entry=0x1010)):
            with self.assertRaises(ValueError):parse_tipa(data,0)

    def test_reject_virtual_overflow_and_overlapping_segments(self):
        with self.assertRaises(ValueError):parse_tipa(self.image(address=0xfffffff8),0)
        data=self.image()[:-8]+b'\x01YSX'+struct.pack('<II',0x1008,16)+bytes(16)+b'\x06YSX'+struct.pack('<I',0x1000)
        with self.assertRaises(ValueError):parse_tipa(data,0)

    def test_wrapper_retains_code_addresses_and_attribute_bytes(self):
        code=bytes(range(32));attrs=b'A-test-attributes'
        raw=wrap_code_elf(code,0xc009dfc0,0xc009dfc0,attrs);elf=Elf(raw)
        self.assertEqual(elf.section('.text')['words'][3],0xc009dfc0)
        self.assertEqual(elf.section('.text')['data'],code)
        self.assertEqual(elf.section('.c6xabi.attributes')['data'],attrs)
        self.assertEqual(struct.unpack_from('<HHI',raw,16),(2,140,1))

class IdentityTests(unittest.TestCase):
    def test_ranges_preserve_gid_and_inclusive_bounds(self):
        rows=registry_ids('## IDs used by other collections\n| gid | fxid | Effects |\n| 8 | 500–502, 957 | demo |\n| 2 | 958 | other |\n')
        self.assertEqual(rows,[(8,[500,501,502,957]),(2,[958])])

    def test_invalid_range_not_silently_ignored(self):
        for ids in ('502-500','70000','500, unknown'):
            with self.assertRaises(ValueError):registry_ids(f'## IDs used by other collections\n| 8 | {ids} | demo |')

    def test_nested_catalogue_preserves_legacy_and_other_groups(self):
        evidence={};scan_json({'legacy':[{'gid':8,'fxid':409}], 'other':{'gid':2,'fxid':958}},evidence,'fixture')
        self.assertEqual(set(evidence),{(8,409),(2,958)})

    def test_inventory_header_reads_both_id_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'fixture.ZDL';b=bytearray(76);b[:8]=b'\0\0\0\0SIZE';b[60]=8;struct.pack_into('<H',b,64,958);p.write_bytes(b)
            self.assertEqual(read_header(p),(8,958))
            p.write_bytes(b[:50])
            with self.assertRaises(ValueError):read_header(p)

if __name__=='__main__':unittest.main()
