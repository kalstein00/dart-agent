"""Install the pinned DART control skill from the bundled archive."""
import argparse
import json
import os
import platform
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

from prepare_release import DEFAULT_LOCK, load, prepare, require, safe_name

ROOT = Path(__file__).resolve().parents[1]


def install(skills_dir, prepared_dir=None, update=False, asset_dir=None, asset_zip=None):
    local_zip = asset_zip is not None
    lock = load(DEFAULT_LOCK)
    compatibility = load(ROOT / 'skills/dart-control/compatibility.json')
    require(compatibility['skillVersion'] == lock['skillVersion'], 'incompatible skill version')
    require(compatibility['dartVersion'] == lock['dartVersion'] and
            compatibility['protocolVersion'] == lock['protocolVersion'], 'incompatible skill DART version/protocol')
    target = skills_dir / 'dart-control'
    require(not target.exists() or update, 'already installed; use --update explicitly')
    skills_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.dart-install-', dir=skills_dir) as temporary:
        work = Path(temporary)
        source = asset_dir or prepared_dir
        if source is None:
            source = work / 'download'
            source.mkdir()
            if asset_zip is None:
                asset_zip = ROOT / 'release/dart-agent-release-assets.zip'
            with zipfile.ZipFile(asset_zip) as archive:
                records = {safe_name(row['file']): row for row in lock['assets']}
                entries = archive.infolist()
                require(len(entries) == len(records) and {item.filename for item in entries} == set(records),
                        'unexpected release archive contents')
                for item in entries:
                    require(item.file_size == records[item.filename]['bytes'], 'release archive size mismatch')
                    with archive.open(item) as response, (source / item.filename).open('wb') as output:
                        shutil.copyfileobj(response, output)
        # Reuse the official asset checks and native execution gate.
        assets = work / 'assets'
        prepare(DEFAULT_LOCK, source, assets)
        candidate = work / 'dart-control'
        shutil.copytree(ROOT / 'skills/dart-control', candidate)
        (candidate / 'bin').mkdir()
        windows = platform.system() == 'Windows'
        shutil.copy2(assets / ('dart-cli-windows-x64.exe' if windows else 'dart-cli-linux-x64'),
                     candidate / 'bin' / ('dart.exe' if windows else 'dart'))
        for name in ('dart-cli-reference.md', 'dart-cli-command-catalog.json', 'dart-agent-distribution.json'):
            shutil.copy2(assets / name, candidate / 'references' / name)
        installation = dict(
            skillVersion=lock['skillVersion'], dartVersion=lock['dartVersion'],
            source='local-release-assets' if asset_dir or local_zip else ('development-prepared-assets' if prepared_dir else 'bundled-archive'),
            upstream=lock['upstream'])
        if lock['upstream'].get('kind') != 'development-candidate':
            installation['release'] = 'kalstein00/dart-agent@v' + lock['skillVersion']
        (candidate / 'installation.json').write_text(json.dumps(installation) + '\n')
        # Personal profiles remain at the official CLI location, outside the
        # managed skill. Roll back a failed replacement.
        backup = work / 'previous'
        if target.exists():
            os.rename(target, backup)
        try:
            os.rename(candidate, target)
        except OSError:
            if backup.exists():
                os.rename(backup, target)
            raise
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-dir', type=Path, default=Path.home() / '.cline/skills')
    sources = parser.add_mutually_exclusive_group()
    sources.add_argument('--prepared-dir', type=Path, help='development only: verified preparation output, not Release proof')
    sources.add_argument('--asset-dir', type=Path, help='local directory containing pinned Release assets')
    sources.add_argument('--asset-zip', type=Path, help='local Release assets ZIP')
    parser.add_argument('--update', action='store_true', help='explicitly replace managed skill files, preserving official profiles')
    args = parser.parse_args()
    try:
        target = install(args.skills_dir.expanduser().absolute(), args.prepared_dir, args.update, args.asset_dir, args.asset_zip)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        print(f'installation failed: {error}', file=sys.stderr)
        return 1
    print(json.dumps(dict(ok=True, skill=str(target), source='local-release-assets' if args.asset_dir or args.asset_zip else ('development-prepared-assets' if args.prepared_dir else 'bundled-archive'))))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
