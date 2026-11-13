#!/usr/bin/env python3
"""Build the portable PC ZIP. Does not access MIDI, USB or any pedal."""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'tools' / 'usb-installer'
NAME = 'FILTER_DELAY_BOOST_PC_v2'
SHA = '26de6cf564784aa0453d54d2dc4cf72f1bc98844010c6285a1a8079a2cafec04'


def build() -> Path:
    output = ROOT / 'downloads' / 'filter-delay-boost-pc-v2'
    output.mkdir(parents=True, exist_ok=True)
    target = output / (NAME + '.zip')
    with tempfile.TemporaryDirectory(prefix='filter-delay-pc-') as temporary:
        package = Path(temporary) / NAME
        package.mkdir()
        # Runtime files, without build-time dependencies, firmware or credentials.
        shutil.copytree(SOURCE / 'dist', package / 'instalador')
        for file in (SOURCE / 'windows').iterdir():
            if file.is_file():
                content = file.read_text(encoding='utf-8')
                # CRLF for native Windows editors; UTF-8 BOM for accented text.
                encoding = 'ascii' if file.suffix.lower() in {'.bat', '.ps1'} else 'utf-8-sig'
                (package / file.name).write_bytes(content.replace('\r\n', '\n').replace('\n', '\r\n').encode(encoding))
        zdl = SOURCE / 'dist' / 'assets' / 'FLTDLBS.ZDL'
        assert hashlib.sha256(zdl.read_bytes()).hexdigest() == SHA
        (package / 'efeito').mkdir()
        shutil.copyfile(zdl, package / 'efeito' / 'FLTDLBS.ZDL')
        manual = (SOURCE / 'windows' / 'MANUAL.txt').read_text(encoding='utf-8')
        title = 'Filter Delay Boost — manual para PC'
        page = ('<!doctype html><html lang="pt-BR"><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>{title}</title><style>body{{max-width:900px;margin:40px auto;'
                'padding:0 24px;font:16px/1.6 system-ui,sans-serif;color:#1b2830;'
                'background:#f5f8f9}pre{white-space:pre-wrap;overflow-wrap:anywhere;'
                'font:inherit}h1{line-height:1.15;color:#125e4e}'
                '@media print{body{margin:0;background:white}}</style>'
                f'<h1>{title}</h1><p>Você pode imprimir este manual ou usar '
                'Ctrl+P → Salvar como PDF.</p><pre>' + html.escape(manual) + '</pre></html>')
        (package / 'MANUAL.html').write_text(page, encoding='utf-8')
        # Include the tracked project sources and evidence, excluding superseded
        # release downloads, Git internals, local proprietary originals and caches.
        tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        allowed = {'src', 'tools', 'tests', 'docs', 'original', 'build'}
        for relative in tracked:
            if not relative:
                continue
            path = Path(relative)
            if path.parts[0] not in allowed and relative not in {'README.md', '.gitignore'}:
                continue
            source = ROOT / path
            if source.is_file():
                destination = package / 'codigo-fonte' / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
        # These newly added packaging sources may not be tracked on first build.
        shutil.copytree(SOURCE / 'windows', package / 'codigo-fonte' / 'tools' / 'usb-installer' / 'windows', dirs_exist_ok=True)
        shutil.copyfile(Path(__file__), package / 'codigo-fonte' / 'tools' / Path(__file__).name)
        metadata = {'package': NAME, 'source_commit': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'candidate_sha256': SHA, 'hardware_tested': False,
            'windows_tested': False, 'local_server_test_platform': 'PowerShell 7 / Linux',
            'note': 'source_commit is the base commit; packaging sources included in codigo-fonte.'}
        (package / 'PACOTE.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
        hashes = ''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(package).as_posix() + '\n'
                         for p in sorted(package.rglob('*')) if p.is_file())
        (package / 'SHA256SUMS.txt').write_text(hashes, encoding='utf-8')
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for file in sorted(package.rglob('*')):
                if file.is_file():
                    entry = zipfile.ZipInfo(file.relative_to(Path(temporary)).as_posix(), (2026, 11, 13, 0, 0, 0))
                    entry.compress_type = zipfile.ZIP_DEFLATED
                    entry.external_attr = 0o100644 << 16
                    archive.writestr(entry, file.read_bytes())
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        prefix = NAME + '/'
        lines = archive.read(prefix + 'SHA256SUMS.txt').decode().splitlines()
        for line in lines:
            expected, relative = line.split('  ', 1)
            assert hashlib.sha256(archive.read(prefix + relative)).hexdigest() == expected, relative
        assert archive.read(prefix + 'efeito/FLTDLBS.ZDL') == zdl.read_bytes()
        assert not any('/.git/' in name or name.endswith('backup-test.zip') for name in archive.namelist())
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (output / 'SHA256SUMS.txt').write_text(digest + '  ' + target.name + '\n', encoding='utf-8')
    print(json.dumps({'zip': str(target), 'bytes': target.stat().st_size, 'files': len(lines) + 1,
                      'sha256': digest, 'zip_crc': 'PASS', 'payload_hashes': 'PASS'}, indent=2))
    return target


if __name__ == '__main__':
    build()
