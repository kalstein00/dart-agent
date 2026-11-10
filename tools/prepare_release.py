"""Prepare pinned official DART assets; no application transport or registry code."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
import tempfile
import zipfile

DEFAULT_LOCK = Path(__file__).resolve().parents[1] / 'release/dart-2.1.1.lock.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(data, record):
    require(len(data) == record['bytes'], f"size mismatch: {record.get('file', record.get('path'))}")
    require(digest(data) == record['sha256'], f"checksum mismatch: {record.get('file', record.get('path'))}")


def safe_name(name):
    require(isinstance(name, str) and name and '/' not in name and '\\' not in name and name not in {'.', '..'},
            'invalid asset filename')
    return name


def identity(document, lock):
    require(document['releaseVersion'] == lock['dartVersion'], 'incompatible DART version')
    require(document['protocolVersion'] == lock['protocolVersion'], 'incompatible protocol version')
    require(document['contract'] == lock['contract'], 'incompatible public contract')


def versioned_identity(response, baseline):
    require(response.get('ok') is True and response.get('protocolVersion') == baseline['protocolVersion'],
            'versioned identity query failed')
    data = response['data']
    require(data['version'] == baseline['releaseVersion'], 'versioned identity release mismatch')
    contract = data['contract']
    for key in ('releaseVersion', 'protocolVersion', 'formatVersion', 'contractVersion', 'fingerprint'):
        require(key in contract and contract[key] == baseline[key], 'versioned identity mismatch: ' + key)


def run_cli(executable, args, protocol_version):
    result = subprocess.run([str(executable), *args], capture_output=True, text=True, encoding='utf-8', timeout=60, check=True)
    response = json.loads(result.stdout)
    require(response.get('ok') is True and response.get('protocolVersion') == protocol_version,
            f'CLI did not report a successful protocol {protocol_version} response')
    return response


def prepare(lock_path, source, output):
    lock = load(lock_path)
    require(source is not None or lock['upstream'].get('kind') != 'development-candidate',
            'development candidate requires local assets; it is not a published release')
    require(lock['schemaVersion'] == 1, 'unsupported distribution schema')
    require((lock['dartVersion'], lock['protocolVersion']) in {('2.1.0', 2), ('2.1.1', 3)},
            'incompatible pinned DART version/protocol')
    protocol_version = lock['protocolVersion']
    require(lock['contract']['formatVersion'] == 2 and
            lock['contract']['fingerprint']['algorithm'] == 'sha256' and
            lock['contract']['fingerprint']['projectionVersion'] == 1, 'incompatible contract format')
    require(not output.exists(), 'output already exists; choose a fresh directory')
    system = platform.system()
    require(system in {'Linux', 'Windows'} and platform.machine().lower() in {'x86_64', 'amd64'},
            'preparation requires Linux or Windows x64 to execute the final CLI')
    platform_key = system.lower() + '-x64'
    records = {safe_name(a['file']): a for a in lock['assets']}
    versioned = lock.get('versionedContract')
    require(protocol_version != 3 or versioned is not None, 'protocol 3 requires a versioned baseline')
    count = 10 if versioned else 7
    require(len(records) == len(lock['assets']) == count, 'unexpected upstream asset inventory')
    if versioned:
        require(set(versioned) == {'releaseVersion', 'protocolVersion', 'formatVersion', 'contractVersion', 'fingerprint'},
                'invalid versioned baseline')
        require(versioned['releaseVersion'] == lock['dartVersion'] and
                versioned['protocolVersion'] == lock['protocolVersion'] and
                versioned['formatVersion'] == lock['contract']['formatVersion'] and
                versioned['fingerprint'] == lock['contract']['fingerprint'] and
                isinstance(versioned['contractVersion'], str) and
                re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', versioned['contractVersion']),
                'incompatible versioned baseline')
        require({'dart-agent-manifest.v2.json', 'dart-cli-command-catalog.v2.json',
                 'dart-cli-reference.v2.md'} <= records.keys(), 'missing versioned assets')
    required = {'dart-agent-manifest.json', 'dart-cli-manifest.json', 'dart-agent-bundle.zip',
                'dart-cli-reference.md', 'dart-cli-command-catalog.json'}
    require(required <= records.keys(), 'missing required manifest/reference assets')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.dart-preparation-', dir=output.parent) as temporary:
        stage = Path(temporary) / 'assets'
        stage.mkdir()
        for name, record in records.items():
            target = stage / name
            if source:
                target.write_bytes((source / name).read_bytes())
            else:
                repository = lock['upstream']['repository']
                with target.open('wb') as stream:
                    subprocess.run(['gh', 'api', '-H', 'Accept: application/octet-stream',
                                    f"repos/{repository}/releases/assets/{record['assetId']}"],
                                   stdout=stream, stderr=subprocess.PIPE, timeout=600, check=True)
            verify(target.read_bytes(), record)
        agent = load(stage / 'dart-agent-manifest.json')
        identity(agent, lock)
        require(agent['agentBundleVersion'] == 1, 'incompatible agent bundle version')
        downloads = {safe_name(a['file']): a for a in agent['downloads']}
        require(len(downloads) == len(agent['downloads']) == 6 and
                set(downloads) == set(records) - {'dart-agent-manifest.json', 'dart-agent-manifest.v2.json', 'dart-cli-command-catalog.v2.json', 'dart-cli-reference.v2.md'}, 'unexpected download inventory')
        for name, record in downloads.items():
            verify((stage / name).read_bytes(), record)
        cli = load(stage / 'dart-cli-manifest.json')
        identity(cli, lock)
        require(cli['formatVersion'] == 1, 'incompatible CLI manifest format')
        platforms = {}
        require(len(cli['artifacts']) == 2, 'expected Linux and Windows CLI artifacts')
        # Upstream standalone manifest has historical names. Resolve public names by
        # immutable bytes/hash from the agent download inventory, never by that name.
        for artifact in cli['artifacts']:
            require(artifact['os'] in {'linux', 'windows'} and artifact['cpu'] == 'x64', 'unsupported CLI platform')
            key = artifact['os'] + '-x64'
            require(key not in platforms, 'duplicate CLI platform')
            require(artifact['libc'] == ('glibc' if artifact['os'] == 'linux' else None), 'unsupported CLI libc')
            matches = [name for name, row in downloads.items()
                       if row['sha256'] == artifact['sha256'] and row['bytes'] == artifact['bytes']]
            require(len(matches) == 1, 'CLI artifact does not match one public download')
            platforms[key] = dict(file=matches[0], os=artifact['os'], cpu='x64', libc=artifact['libc'])
        require(set(platforms) == {'linux-x64', 'windows-x64'}, 'missing CLI platform')
        catalog = load(stage / 'dart-cli-command-catalog.json')
        require(catalog['releaseVersion'] == lock['dartVersion'] and catalog['protocolVersion'] == protocol_version and
                catalog['formatVersion'] == lock['contract']['formatVersion'] and
                catalog['fingerprint'] == lock['contract']['fingerprint'], 'incompatible command catalog')
        with zipfile.ZipFile(stage / 'dart-agent-bundle.zip') as archive:
            names = archive.namelist()
            require(len(names) == len(set(names)) and 'manifest.json' in names, 'invalid bundle inventory')
            bundle = json.loads(archive.read('manifest.json'))
            identity(bundle, lock)
            require(bundle['agentBundleVersion'] == 1 and bundle['standalone'] == cli, 'incompatible bundled CLI identity')
            files = {row['path']: row for row in bundle['files']}
            require(len(files) == len(bundle['files']) and set(names) == set(files) | {'manifest.json'},
                    'unexpected bundled files')
            for name, row in files.items():
                path = PurePosixPath(name)
                require(not path.is_absolute() and '..' not in path.parts and '\\' not in name,
                        'unsafe bundle path')
                require(archive.getinfo(name).file_size == row['bytes'], 'bundle size mismatch')
                verify(archive.read(name), row)
            require(archive.read('Reference.md') == (stage / 'dart-cli-reference.md').read_bytes() and
                    archive.read('catalog.json') == (stage / 'dart-cli-command-catalog.json').read_bytes(),
                    'bundled public reference/catalog mismatch')
        if versioned:
            manifest_v2 = load(stage / 'dart-agent-manifest.v2.json')
            require(manifest_v2['manifestVersion'] == 2 and manifest_v2['status'] == 'candidate' and
                    manifest_v2['contract'] == versioned and
                    manifest_v2['candidateId'] == lock['candidateId'] and
                    manifest_v2['source'] == lock['candidateSource'],
                    'versioned candidate identity mismatch')
            verify((stage / 'dart-agent-manifest.json').read_bytes(), manifest_v2['legacy'])
            versioned_catalog = load(stage / 'dart-cli-command-catalog.v2.json')
            require(versioned_catalog['contractVersion'] == versioned['contractVersion'] and
                    {k: versioned_catalog[k] for k in ('releaseVersion', 'protocolVersion', 'formatVersion', 'fingerprint')} ==
                    {k: versioned[k] for k in ('releaseVersion', 'protocolVersion', 'formatVersion', 'fingerprint')},
                    'versioned catalog identity mismatch')
        executable = stage / platforms[platform_key]['file']
        if system == 'Linux':
            executable.chmod(0o755)
        version = run_cli(executable, ['version'], protocol_version)
        require(version['data']['version'] == lock['dartVersion'], 'executing CLI version mismatch')
        observed = run_cli(executable, ['contract', 'identity'], protocol_version)
        require(observed['data']['version'] == lock['dartVersion'], 'executing CLI identity version mismatch')
        live_contract = observed['data']['contract']
        require(live_contract['releaseVersion'] == lock['dartVersion'] and
                live_contract['protocolVersion'] == lock['protocolVersion'] and
                {key: live_contract[key] for key in ('formatVersion', 'fingerprint')} == lock['contract'],
                'executing CLI public identity mismatch')
        exported = run_cli(executable, ['contract', 'export', 'full'], protocol_version)
        require(exported['data'] == catalog, 'executing CLI public contract differs from catalog')
        if versioned:
            observed_v2 = run_cli(executable, ['contract', 'identity', 'versioned'], protocol_version)
            versioned_identity(observed_v2, versioned)
            exported_v2 = run_cli(executable, ['contract', 'export', 'versioned'], protocol_version)
            require(exported_v2['data'] == versioned_catalog, 'versioned CLI export differs from catalog')
        # Keep private host paths out of published preparation evidence.
        observed['data'].pop('executablePath', None)
        observed['data'].pop('entryPath', None)
        distribution = dict(schemaVersion=1, skillVersion=lock['skillVersion'], dartVersion=lock['dartVersion'],
                            protocolVersion=lock['protocolVersion'], contract=lock['contract'],
                            upstream=lock['upstream'], platforms=platforms,
                            assets=[{k: row[k] for k in ('file', 'bytes', 'sha256')} for row in lock['assets']],
                            verification={system.lower(): dict(system=system, machine=platform.machine(),
                                                               version=version, identity=observed, catalogMatches=True),
                                          ('windows' if system == 'Linux' else 'linux'):
                                              'integrity-only; native execution not performed'})
        if versioned:
            distribution['versionedContract'] = versioned
            distribution['candidateId'] = lock['candidateId']
            distribution['candidateSource'] = lock['candidateSource']
            observed_v2['data'].pop('executablePath', None)
            observed_v2['data'].pop('entryPath', None)
            distribution['verification'][system.lower()]['versionedIdentity'] = observed_v2
        (stage / 'dart-agent-distribution.json').write_text(json.dumps(distribution, indent=2) + '\n', encoding='utf-8')
        # Publish only after every check succeeds; a failed run leaves no usable candidate.
        os.rename(stage, output)
    return distribution


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock', type=Path, default=DEFAULT_LOCK, help='trusted lock file (default: repository pin)')
    parser.add_argument('--source-dir', type=Path, help='use an already downloaded official asset directory')
    parser.add_argument('--output', type=Path, required=True, help='new output directory for individual Release attachments')
    args = parser.parse_args()
    try:
        result = prepare(args.lock, args.source_dir, args.output.absolute())
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        print(f'preparation failed: {error}', file=sys.stderr)
        return 1
    print(json.dumps(dict(ok=True, output=str(args.output), dartVersion=result['dartVersion'],
                          skillVersion=result['skillVersion'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
