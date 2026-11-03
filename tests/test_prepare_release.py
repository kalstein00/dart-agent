"""Exercise release preparation through its maintainer-facing CLI."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'tools/prepare_release.py'
CONTRACT = {'formatVersion': 2, 'fingerprint': {'algorithm': 'sha256', 'projectionVersion': 1, 'value': 'a' * 64}}


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'source'
        self.source.mkdir()
        self.output = self.base / 'release'
        self.catalog = dict(formatVersion=2, releaseVersion='2.1.0', protocolVersion=2,
                            fingerprint=CONTRACT['fingerprint'], commands=[{'name': 'version'}])
        identity = dict(version='2.1.0', contract=dict(CONTRACT, releaseVersion='2.1.0', protocolVersion=2))
        # Executable fixture models the external official CLI, never our implementation.
        responses = {'version': {'version': '2.1.0'}, 'contract identity': identity,
                     'contract export full': self.catalog}
        script = '#!/bin/sh\ncase "$*" in\n'
        for command, data in responses.items():
            value = json.dumps(dict(ok=True, protocolVersion=2, data=data))
            script += f"'{command}') printf '%s\\n' '{value}';;\n"
        script += '*) exit 1;;\nesac\n'
        self.write('dart-cli-linux-x64', script.encode())
        self.write('dart-cli-windows-x64.exe', b'fixture Windows executable')
        self.write('dart-cli-reference.md', b'public command reference')
        self.write('dart-cli-command-catalog.json', json.dumps(self.catalog).encode())
        artifacts = []
        for name, os_name in [('dart-cli-linux-x64', 'linux'), ('dart-cli-windows-x64.exe', 'windows')]:
            artifacts.append(dict(self.record(name), file='historical-' + os_name,
                                  os=os_name, cpu='x64', libc='glibc' if os_name == 'linux' else None))
        common = dict(releaseVersion='2.1.0', protocolVersion=2, contract=CONTRACT)
        cli_manifest = dict(common, formatVersion=1, artifacts=artifacts)
        self.write('dart-cli-manifest.json', json.dumps(cli_manifest).encode())
        bundle_files = {'Guide.md': b'public guidance', 'Reference.md': b'public command reference',
                        'catalog.json': json.dumps(self.catalog).encode()}
        manifest = dict(common, agentBundleVersion=1, standalone=cli_manifest,
                        files=[dict(path=n, bytes=len(b), sha256=hashlib.sha256(b).hexdigest())
                               for n, b in bundle_files.items()])
        with zipfile.ZipFile(self.source / 'dart-agent-bundle.zip', 'w') as archive:
            for name, data in bundle_files.items():
                archive.writestr(name, data)
            archive.writestr('manifest.json', json.dumps(manifest))
        agent = dict(common, agentBundleVersion=1, downloads=[self.record(p.name) for p in self.source.iterdir()])
        self.write('dart-agent-manifest.json', json.dumps(agent).encode())
        lock = dict(schemaVersion=1, skillVersion='0.1.0', dartVersion='2.1.0', protocolVersion=2,
                    contract=CONTRACT, upstream=dict(repository='kalstein00/DART', tag='v2.1.0'),
                    assets=[dict(self.record(p.name), assetId=i) for i, p in enumerate(self.source.iterdir())])
        self.lock = self.base / 'lock.json'
        self.lock.write_text(json.dumps(lock))

    def write(self, name, data):
        (self.source / name).write_bytes(data)

    def record(self, name):
        data = (self.source / name).read_bytes()
        return dict(file=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

    def run_tool(self):
        return subprocess.run(['uv', 'run', '--no-project', 'python', str(TOOL),
                               '--lock', str(self.lock), '--source-dir', str(self.source),
                               '--output', str(self.output)], capture_output=True, text=True)

    def test_prepares_verified_assets_and_independent_skill_version(self):
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stderr)
        distribution = json.loads((self.output / 'dart-agent-distribution.json').read_text())
        self.assertEqual(distribution['skillVersion'], '0.1.0')
        self.assertEqual(distribution['dartVersion'], '2.1.0')
        self.assertEqual(distribution['platforms']['linux-x64']['file'], 'dart-cli-linux-x64')
        self.assertEqual(distribution['platforms']['windows-x64']['file'], 'dart-cli-windows-x64.exe')
        self.assertEqual(distribution['verification']['linux']['version']['data']['version'], '2.1.0')
        self.assertEqual(len(distribution['assets']), 7)
        self.assertEqual(set(p.name for p in self.output.iterdir()),
                         {p.name for p in self.source.iterdir()} | {'dart-agent-distribution.json'})

    def test_checksum_mismatch_never_publishes_candidate(self):
        path = self.source / 'dart-cli-reference.md'
        path.write_bytes(b'x' * path.stat().st_size)
        result = self.run_tool()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('checksum mismatch', result.stderr)
        self.assertFalse(self.output.exists())

    def test_missing_download_never_publishes_candidate(self):
        (self.source / 'dart-cli-windows-x64.exe').unlink()
        result = self.run_tool()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('preparation failed', result.stderr)
        self.assertFalse(self.output.exists())

    def test_incompatible_pinned_version_is_rejected(self):
        lock = json.loads(self.lock.read_text())
        lock['dartVersion'] = '2.0.0'
        self.lock.write_text(json.dumps(lock))
        result = self.run_tool()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('incompatible pinned DART version', result.stderr)
        self.assertFalse(self.output.exists())

    def test_verified_manifest_with_wrong_release_is_rejected(self):
        agent_path = self.source / 'dart-agent-manifest.json'
        agent = json.loads(agent_path.read_text())
        agent['releaseVersion'] = '2.0.0'
        agent_path.write_text(json.dumps(agent))
        lock = json.loads(self.lock.read_text())
        for row in lock['assets']:
            if row['file'] == agent_path.name:
                row.update(self.record(agent_path.name))
        self.lock.write_text(json.dumps(lock))
        result = self.run_tool()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('incompatible DART version', result.stderr)
        self.assertFalse(self.output.exists())

    def test_existing_output_is_preserved(self):
        self.output.mkdir()
        (self.output / 'keep').write_text('previous candidate')
        result = self.run_tool()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.output / 'keep').read_text(), 'previous candidate')

    def test_download_failure_never_publishes_candidate(self):
        import os
        command_dir = self.base / 'bin'
        command_dir.mkdir()
        gh = command_dir / 'gh'
        gh.write_text('#!/bin/sh\necho "fixture download unavailable" >&2\nexit 1\n')
        gh.chmod(0o755)
        result = subprocess.run(['uv', 'run', '--no-project', 'python', str(TOOL),
                                 '--lock', str(self.lock), '--output', str(self.output)],
                                capture_output=True, text=True,
                                env=dict(os.environ, PATH=str(command_dir) + os.pathsep + os.environ['PATH']))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('preparation failed', result.stderr)
        self.assertFalse(self.output.exists())

    def test_final_executable_reporting_wrong_version_is_rejected(self):
        executable = self.source / 'dart-cli-linux-x64'
        executable.write_text(executable.read_text().replace('2.1.0', '2.0.0'))
        cli_path = self.source / 'dart-cli-manifest.json'
        cli = json.loads(cli_path.read_text())
        for artifact in cli['artifacts']:
            if artifact['os'] == 'linux':
                artifact.update({key: self.record(executable.name)[key] for key in ('bytes', 'sha256')})
        cli_path.write_text(json.dumps(cli))
        bundle_path = self.source / 'dart-agent-bundle.zip'
        with zipfile.ZipFile(bundle_path) as archive:
            contents = {name: archive.read(name) for name in archive.namelist()}
        bundled = json.loads(contents['manifest.json'])
        bundled['standalone'] = cli
        contents['manifest.json'] = json.dumps(bundled).encode()
        with zipfile.ZipFile(bundle_path, 'w') as archive:
            for name, content in contents.items():
                archive.writestr(name, content)
        agent_path = self.source / 'dart-agent-manifest.json'
        agent = json.loads(agent_path.read_text())
        agent['downloads'] = [self.record(row['file']) for row in agent['downloads']]
        agent_path.write_text(json.dumps(agent))
        lock = json.loads(self.lock.read_text())
        for row in lock['assets']:
            row.update(self.record(row['file']))
        self.lock.write_text(json.dumps(lock))
        result = self.run_tool()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('executing CLI version mismatch', result.stderr)
        self.assertFalse(self.output.exists())
