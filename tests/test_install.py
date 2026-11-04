"""Public clone-install entry point; real prepared assets are supplied per test."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def test_missing_release_fails_without_installing_a_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = subprocess.run(['uv', 'run', '--no-project', 'python', str(ROOT / 'tools/install.py'), '--skills-dir', str(root / 'skills')],
                                    env={**os.environ, 'https_proxy': 'http://127.0.0.1:1', 'no_proxy': ''}, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('installation failed', result.stderr)
            self.assertFalse((root / 'skills/dart-control').exists())

    def test_update_is_explicit_and_preserves_existing_installation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / 'skills/dart-control'
            target.mkdir(parents=True)
            (target / 'keep').write_text('existing installation')
            result = subprocess.run(['uv', 'run', '--no-project', 'python', str(ROOT / 'tools/install.py'), '--skills-dir', str(root / 'skills')],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('use --update explicitly', result.stderr)
            self.assertEqual((target / 'keep').read_text(), 'existing installation')

    def test_corrupt_prepared_assets_leave_existing_skill_usable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / 'skills/dart-control'
            target.mkdir(parents=True)
            (target / 'keep').write_text('existing installation')
            source = root / 'source'
            source.mkdir()
            (source / 'dart-cli-linux-x64').write_text('untrusted executable')
            result = subprocess.run(['uv', 'run', '--no-project', 'python', str(ROOT / 'tools/install.py'), '--skills-dir', str(root / 'skills'),
                                     '--asset-dir', str(source), '--update'], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((target / 'keep').read_text(), 'existing installation')

    def test_clone_install_and_update_keep_official_profiles_outside_skill(self):
        import json
        import shutil
        from test_prepare_release import PreparationTests
        fixture = PreparationTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        clone = fixture.base / 'clone'
        (clone / 'release').mkdir(parents=True)
        shutil.copytree(ROOT / 'tools', clone / 'tools')
        shutil.copytree(ROOT / 'skills', clone / 'skills')
        shutil.copy2(fixture.lock, clone / 'release/dart-2.1.0.lock.json')
        home = fixture.base / 'home'
        profiles = home / '.dart/connections'
        profiles.mkdir(parents=True)
        (profiles / 'personal.json').write_text('private-profile-marker')
        command = ['uv', 'run', '--no-project', 'python', str(clone / 'tools/install.py'), '--prepared-dir', str(fixture.source)]
        env = {**os.environ, 'HOME': str(home)}
        for arguments in ([], ['--update']):
            result = subprocess.run(command + arguments, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = home / '.cline/skills/dart-control'
            self.assertTrue((installed / 'SKILL.md').is_file())
            version = subprocess.run([str(installed / 'bin/dart'), 'version'], capture_output=True, text=True)
            self.assertEqual(json.loads(version.stdout)['data']['version'], '2.1.0')
            self.assertEqual(json.loads((installed / 'installation.json').read_text())['source'], 'development-prepared-assets')
            self.assertEqual((profiles / 'personal.json').read_text(), 'private-profile-marker')
            self.assertFalse(any('private-profile-marker' in p.read_text(errors='ignore') for p in installed.rglob('*') if p.is_file()))

    def test_update_rejects_skill_version_mismatched_with_release_lock(self):
        import json
        import shutil
        from test_prepare_release import PreparationTests
        fixture = PreparationTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        clone = fixture.base / 'clone'
        (clone / 'release').mkdir(parents=True)
        shutil.copytree(ROOT / 'tools', clone / 'tools')
        shutil.copytree(ROOT / 'skills', clone / 'skills')
        lock = json.loads(fixture.lock.read_text())
        lock['skillVersion'] = '9.9.9'
        (clone / 'release/dart-2.1.0.lock.json').write_text(json.dumps(lock))
        target = fixture.base / 'skills/dart-control'
        target.mkdir(parents=True)
        (target / 'keep').write_text('existing installation')
        result = subprocess.run(['uv', 'run', '--no-project', 'python', str(clone / 'tools/install.py'),
                                 '--skills-dir', str(target.parent), '--prepared-dir', str(fixture.source), '--update'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('incompatible skill version', result.stderr)
        self.assertEqual((target / 'keep').read_text(), 'existing installation')

    def test_checksum_failure_during_update_preserves_skill_and_profile(self):
        from test_prepare_release import PreparationTests
        fixture = PreparationTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        import shutil
        clone = fixture.base / 'clone'
        (clone / 'release').mkdir(parents=True)
        shutil.copytree(ROOT / 'tools', clone / 'tools')
        shutil.copytree(ROOT / 'skills', clone / 'skills')
        shutil.copy2(fixture.lock, clone / 'release/dart-2.1.0.lock.json')
        home = fixture.base / 'home'
        target = home / '.cline/skills/dart-control'
        target.mkdir(parents=True)
        (target / 'keep').write_text('existing')
        profile = home / '.dart/connections/personal.json'
        profile.parent.mkdir(parents=True)
        profile.write_text('private-profile-marker')
        asset = fixture.source / 'dart-cli-linux-x64'
        data = asset.read_bytes()
        asset.write_bytes(bytes([data[0] ^ 1]) + data[1:])
        result = subprocess.run(['uv', 'run', '--no-project', 'python', str(clone / 'tools/install.py'),
                                 '--prepared-dir', str(fixture.source), '--update'],
                                env={**os.environ, 'HOME': str(home)}, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('checksum mismatch', result.stderr)
        self.assertEqual((target / 'keep').read_text(), 'existing')
        self.assertEqual(profile.read_text(), 'private-profile-marker')

    def test_download_failure_during_update_preserves_skill_and_profile(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            target = home / '.cline/skills/dart-control'
            target.mkdir(parents=True)
            (target / 'keep').write_text('existing')
            profile = home / '.dart/connections/personal.json'
            profile.parent.mkdir(parents=True)
            profile.write_text('private-profile-marker')
            result = subprocess.run(['uv', 'run', '--no-project', 'python', str(ROOT / 'tools/install.py'), '--update'],
                                    env={**os.environ, 'HOME': str(home), 'https_proxy': 'http://127.0.0.1:1', 'no_proxy': ''},
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('installation failed', result.stderr)
            self.assertEqual((target / 'keep').read_text(), 'existing')
            self.assertEqual(profile.read_text(), 'private-profile-marker')
