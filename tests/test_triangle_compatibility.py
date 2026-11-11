"""Wave=0 must preserve the audio of the version the owner tested."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from triangle_fixture import fingerprints

ROOT=Path(__file__).resolve().parents[1]


class TriangleCompatibilityTest(unittest.TestCase):
    @unittest.skipUnless(sys.byteorder=='little','fixture is little-endian float32')
    def test_triangle_audio_is_bit_exact_to_v1(self):
        work=ROOT/'work/tests';work.mkdir(parents=True,exist_ok=True)
        library=work/'triangle-current.so'
        subprocess.run(['cc','-std=c99','-O2','-ffp-contract=off','-fPIC','-shared',
                        str(ROOT/'src/phsdepth_dsp.c'),'-o',str(library)],check=True)
        baseline=json.loads((ROOT/'tests/triangle-v1.00.json').read_text())
        self.assertEqual(fingerprints(library),baseline['cases'])
