import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validate_zdl',ROOT/'tools/validate_zdl.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class ZdlTests(unittest.TestCase):
    def setUp(self):
        self.data=(ROOT/'dist/PhsDepth.ZDL').read_bytes()
        self.manifest=json.loads((ROOT/'zoom/manifest_pedal.json').read_text())

    def test_real_artifact_structure(self):
        result=module.validate(self.data,self.manifest)
        self.assertTrue(result['structurally_valid'])
        report=json.loads((ROOT/'dist/build-report.json').read_text())
        self.assertEqual(result['sha256'],report['sha256'])
        self.assertFalse(report['audio_nop'])
        self.assertFalse(report['physically_tested'])
        self.assertTrue(report['own_runtime'])
        self.assertTrue(report['materialize_init'])

    def test_emulator_evidence_matches_artifact(self):
        report=json.loads((ROOT/'dist/emulator-report.json').read_text())
        self.assertTrue(report['passed'])
        self.assertEqual(report['artifact_sha256'],hashlib.sha256(self.data).hexdigest())
        self.assertFalse(report['physical_hardware_test'])
        self.assertEqual(report['cases'],252)
        self.assertEqual([p['name'] for p in self.manifest['params']],['Rate','Color','Level','Depth','Wave'])
        self.assertEqual(self.manifest['params'][4]['default'],0)

    def test_identity_audit(self):
        audit=json.loads((ROOT/'docs/id-audit.json').read_text())
        self.assertEqual(audit['candidate'],{'gid':self.manifest['gid'],'fxid':self.manifest['fxid']})
        self.assertTrue(audit['clear_in_audited_sources'])
        self.assertFalse(audit['conflicts'])
        self.assertFalse(audit['same_fxid_any_group'])
        self.assertEqual(len(audit['repositories']),7)

    def test_reject_truncated_binary(self):
        with self.assertRaisesRegex(ValueError,'length mismatch'):
            module.validate(self.data[:-1],self.manifest)

    def test_reject_factory_identity(self):
        data=bytearray(self.data);data[64:66]=bytes([16,0])
        with self.assertRaisesRegex(ValueError,'identity mismatch'):
            module.validate(data,self.manifest)

    def test_reject_wrong_architecture(self):
        data=bytearray(self.data);data[76+18:76+20]=bytes([62,0])
        with self.assertRaisesRegex(ValueError,'C6000'):
            module.validate(data,self.manifest)

    def test_reject_invalid_control_range(self):
        m=json.loads(json.dumps(self.manifest));m['params'][1]['max']=100
        with self.assertRaisesRegex(ValueError,'range/default mismatch'):
            module.validate(self.data,m)
