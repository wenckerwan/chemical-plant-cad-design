"""Functional acceptance checks for the relocatable installer (standard library)."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

INSTALLER = Path(os.environ.get('CHEM_INSTALLER', str(Path(__file__).resolve().parents[1] / 'install.py')))
NAME = 'chemical-plant-cad-design'


def manifest(root):
    files = {}
    for p in root.rglob('*'):
        if p.is_file() and p.name != 'manifest.json':
            files[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    (root / 'manifest.json').write_text(json.dumps({'format': 1, 'skill_name': NAME, 'version': '1.0.0', 'files': files}), encoding='utf-8')


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='chem-skill-test-')
        self.root = Path(self.tmp.name)
        self.pkg = self.root / 'moved package 化工'
        self.pkg.mkdir()
        # Source is intentionally relocated, never installed from its build path.
        if INSTALLER.exists():
            shutil.copy2(INSTALLER, self.pkg / 'install.py')
        self.skill = self.pkg / 'skills' / NAME
        (self.skill / 'references').mkdir(parents=True)
        (self.skill / 'SKILL.md').write_text('---\nname: '+NAME+'\ndescription: Chemical CAD reference\n---\nRead [rules](references/rules.md).\n', encoding='utf-8')
        (self.skill / 'references' / 'rules.md').write_text('# Rules\n项目约定\n', encoding='utf-8')
        self.dest = self.root / 'new user 中文' / 'skills'
        manifest(self.pkg)

    def tearDown(self):
        self.tmp.cleanup()

    def run_install(self, *args, env=None):
        active_env = os.environ.copy()
        active_env['PYTHONUTF8'] = '1'
        if env:
            active_env.update(env)
        return subprocess.run([sys.executable, str(self.pkg / 'install.py'), *args], capture_output=True, text=True, encoding='utf-8', env=active_env)

    def assert_rejected(self, result):
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stderr)['status'], 'error')

    def test_relocated_dry_run_does_not_create_target(self):
        r = self.run_install('--target', str(self.dest), '--dry-run')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(self.dest.exists())
        self.assertEqual(json.loads(r.stdout)['status'], 'dry-run')

    def test_install_contains_independent_reference_and_is_idempotent(self):
        r = self.run_install('--target', str(self.dest))
        self.assertEqual(r.returncode, 0, r.stderr)
        placed = self.dest / NAME
        self.assertEqual((placed / 'references/rules.md').read_bytes(), (self.skill / 'references/rules.md').read_bytes())
        r = self.run_install('--target', str(self.dest))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'], 'unchanged')

    def test_modified_installation_is_not_overwritten(self):
        self.assertEqual(self.run_install('--target', str(self.dest)).returncode, 0)
        target = self.dest / NAME / 'references/rules.md'
        target.write_text('user edits', encoding='utf-8')
        r = self.run_install('--target', str(self.dest))
        self.assert_rejected(r)
        self.assertEqual(target.read_text(encoding='utf-8'), 'user edits')

    def test_corrupt_package_is_rejected_before_write(self):
        (self.skill / 'references/rules.md').write_text('corruption', encoding='utf-8')
        r = self.run_install('--target', str(self.dest))
        self.assert_rejected(r)
        self.assertFalse(self.dest.exists())

    def test_codex_profile_respects_current_environment(self):
        custom_home = self.root / 'custom codex home'
        r = self.run_install('--profile', 'codex', '--dry-run', env={'CODEX_HOME': str(custom_home)})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(Path(json.loads(r.stdout)['destination']), (custom_home / 'skills' / NAME).resolve())

    def test_cannot_install_inside_source_package(self):
        r = self.run_install('--target', str(self.pkg / 'skills' / 'nested'))
        self.assert_rejected(r)
        self.assertFalse((self.pkg / 'skills' / 'nested').exists())

    def test_manifest_path_traversal_is_rejected(self):
        data = json.loads((self.pkg / 'manifest.json').read_text(encoding='utf-8'))
        data['files']['../outside.txt'] = '0' * 64
        (self.pkg / 'manifest.json').write_text(json.dumps(data), encoding='utf-8')
        r = self.run_install('--target', str(self.dest))
        self.assert_rejected(r)
        self.assertFalse(self.dest.exists())

    def test_unmanifested_payload_is_rejected(self):
        (self.skill / 'unexpected.py').write_text('print(1)', encoding='utf-8')
        r = self.run_install('--target', str(self.dest))
        self.assert_rejected(r)
        self.assertFalse(self.dest.exists())

    def test_broken_reference_is_rejected(self):
        (self.skill / 'SKILL.md').write_text('---\nname: '+NAME+'\ndescription: Test\n---\nRead [missing](references/missing.md).\n', encoding='utf-8')
        manifest(self.pkg)
        r = self.run_install('--target', str(self.dest))
        self.assert_rejected(r)
        self.assertFalse(self.dest.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)

