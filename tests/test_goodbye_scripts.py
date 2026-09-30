"""Offline safety model of the TTL subset used by the goodbye templates.

This does not validate the camera's TTL implementation or storage behavior.
"""
import re
import unittest
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parents[1] / 'examples'
CAMERA = r'A:\Resource\Jpeg\GoodBye.jpg'
BACKUP = r'C:\GBBACK.JPG'
NEW = r'C:\NEWGB.JPG'
READ = r'C:\GBREAD.JPG'
REST = r'C:\GBREST.JPG'


def run_script(name, files, fail_copy=False):
    result = 0
    active = True
    writes = []
    for raw in (EXAMPLES / f'{name}-goodbye.ttl.example').read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith(';'):
            continue
        if line == 'endif':
            active = True
            continue
        if line.startswith('if '):
            match = re.fullmatch(r'if result = ([01]) then', line)
            if not match:
                raise AssertionError(f'Unsupported condition: {line}')
            active = result == int(match[1])
            continue
        if not active:
            continue
        if line == 'exit':
            break
        search = re.fullmatch(r"filesearch '([^']+)'", line)
        copy = re.fullmatch(r"filecopy '([^']+)' '([^']+)'", line)
        if search:
            result = int(search[1] in files)
        elif copy:
            source, target = copy.groups()
            if source in files and not fail_copy:
                files[target] = files[source]
                writes.append(target)
        else:
            raise AssertionError(f'Unsupported command: {line}')
    return writes


class GoodbyeSafetyTests(unittest.TestCase):
    def test_backup_preserved_after_replacement_and_repeated_boot(self):
        files = {CAMERA: b'original', NEW: b'custom'}
        run_script('backup', files)
        run_script('write', files)
        self.assertEqual(files[CAMERA], b'custom')
        self.assertEqual(files[READ], b'custom')
        self.assertEqual(run_script('backup', files), [])
        self.assertEqual(run_script('write', files), [])
        self.assertEqual(files[BACKUP], b'original')
        run_script('restore', files)
        self.assertEqual(files[CAMERA], b'original')
        self.assertEqual(files[REST], files[BACKUP])
        self.assertEqual(run_script('restore', files), [])

    def test_missing_inputs_never_write_camera(self):
        for name, files in [
            ('backup', {}),
            ('write', {CAMERA: b'original', NEW: b'custom'}),
            ('write', {CAMERA: b'original', BACKUP: b'original'}),
            ('restore', {CAMERA: b'custom'}),
        ]:
            with self.subTest(name=name, files=files):
                before = files.copy()
                self.assertEqual(run_script(name, files), [])
                self.assertEqual(files, before)

    def test_failed_backup_prevents_later_write(self):
        files = {CAMERA: b'original', NEW: b'custom'}
        run_script('backup', files, fail_copy=True)
        self.assertEqual(run_script('write', files), [])
        self.assertEqual(files[CAMERA], b'original')

    def test_existing_readbacks_block_even_with_changed_source(self):
        for name, output in [('write', READ), ('restore', REST)]:
            files = {CAMERA: b'current', BACKUP: b'original',
                     NEW: b'new', output: b'previous readback'}
            with self.subTest(name=name):
                before = files.copy()
                self.assertEqual(run_script(name, files), [])
                self.assertEqual(files, before)


if __name__ == '__main__':
    unittest.main()
