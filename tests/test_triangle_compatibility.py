"""Preserve the Triangle and Sine audio approved by the owner."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from triangle_fixture import fingerprints

ROOT=Path(__file__).resolve().parents[1]


class TriangleCompatibilityTest(unittest.TestCase):
    @unittest.skipUnless(sys.byteorder=='little','fixture is little-endian float32')
    def test_three_waves_at_fixed_hz_remain_bit_exact(self):
        work=ROOT/'work/tests';work.mkdir(parents=True,exist_ok=True)
        library=work/'triangle-current.so'
        subprocess.run(['cc','-std=c99','-O2','-ffp-contract=off','-fPIC','-shared',
                        str(ROOT/'src/phsdepth_dsp.c'),'-o',str(library)],check=True)
        baseline=json.loads((ROOT/'tests/triangle-v1.00.json').read_text())
        self.assertEqual(fingerprints(library),baseline['cases'])
        sine=json.loads((ROOT/'tests/sine-v1.11.json').read_text())
        self.assertEqual(fingerprints(library,1),sine['cases'])
        step=json.loads((ROOT/'tests/step-v1.20.json').read_text())
        self.assertEqual(fingerprints(library,2),step['cases'])
