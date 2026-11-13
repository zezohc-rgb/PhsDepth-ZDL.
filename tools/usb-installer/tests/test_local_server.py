"""HTTP tests only; no browser, USB or MIDI. Requires PowerShell 7 in PATH."""
import hashlib
import http.client
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import tempfile
import threading
import unittest


class LocalServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        executable = os.environ.get('FDB_PWSH') or shutil.which('pwsh')
        if not executable:
            raise unittest.SkipTest('PowerShell unavailable; launcher not tested here')
        source = Path(__file__).resolve().parents[1]
        cls.temp = tempfile.TemporaryDirectory(prefix='fdb pacote com espacos ')
        cls.root = Path(cls.temp.name)
        shutil.copytree(source / 'dist', cls.root / 'instalador')
        shutil.copyfile(source / 'windows' / 'SERVIDOR_LOCAL.ps1', cls.root / 'SERVIDOR_LOCAL.ps1')
        (cls.root / 'outside.txt').write_text('must never be served')
        cls.process = subprocess.Popen([executable, '-NoLogo', '-NoProfile', '-File',
                                       str(cls.root / 'SERVIDOR_LOCAL.ps1'), '-SemNavegador'],
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        messages = queue.Queue()
        def output():
            for line in cls.process.stdout:
                messages.put(line)
            messages.put(None)
        threading.Thread(target=output, daemon=True).start()
        logs = []
        while True:
            try:
                line = messages.get(timeout=20)
            except queue.Empty:
                cls.process.terminate()
                raise AssertionError('Server failed to start: ' + ''.join(logs))
            logs.append(line)
            if line is None:
                cls.process.wait(timeout=5)
                cls.process.stdout.close()
                cls.temp.cleanup()
                raise AssertionError('Server exited before opening a port: ' + ''.join(logs[:-1]))
            match = re.search(r'http://127\.0\.0\.1:(\d+)/', line)
            if match:
                cls.port = int(match[1])
                break

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.wait(timeout=10)
        cls.process.stdout.close()
        cls.temp.cleanup()

    def request(self, path, method='GET'):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=10)
        connection.request(method, path)
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result

    def test_index(self):
        status, headers, data = self.request('/')
        self.assertEqual(status, 200)
        self.assertIn('text/html', headers['Content-Type'])
        self.assertIn(b'app.mjs', data)

    def test_javascript_mime(self):
        status, headers, data = self.request('/app.mjs?v=1')
        self.assertEqual(status, 200)
        self.assertIn('javascript', headers['Content-Type'])
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(headers['Cache-Control'], 'no-store')

    def test_zdl_exact_hash(self):
        status, headers, data = self.request('/assets/FLTDLBS.ZDL')
        self.assertEqual(status, 200)
        self.assertEqual(len(data), 18708)
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         '26de6cf564784aa0453d54d2dc4cf72f1bc98844010c6285a1a8079a2cafec04')

    def test_head_has_length_but_no_body(self):
        status, headers, data = self.request('/assets/FLTDLBS.ZDL', 'HEAD')
        self.assertEqual(status, 200)
        self.assertEqual(int(headers['Content-Length']), 18708)
        self.assertEqual(data, b'')

    def test_path_escape_blocked(self):
        for path in ['/../outside.txt', '/%2e%2e/outside.txt', '/%2e%2e%5coutside.txt', '/C:%5cWindows', '/%00']:
            with self.subTest(path=path):
                self.assertEqual(self.request(path)[0], 403)

    def test_missing_file(self):
        self.assertEqual(self.request('/missing')[0], 404)

    def test_post_blocked_and_server_still_works(self):
        self.assertEqual(self.request('/', 'POST')[0], 405)
        self.assertEqual(self.request('/')[0], 200)


if __name__ == '__main__':
    unittest.main(verbosity=2)
