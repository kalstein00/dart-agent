"""Install the pinned DART control skill from dart-agent Release attachments."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import urlopen

from prepare_release import DEFAULT_LOCK, load, prepare, require, safe_name

ROOT = Path(__file__).resolve().parents[1]


def install(skills_dir, prepared_dir=None, update=False, asset_dir=None):
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
            for row in lock['assets']:
                name = safe_name(row['file'])
                url = ('https://github.com/kalstein00/dart-agent/releases/download/' +
                       quote('v' + lock['skillVersion'], safe='') + '/' + quote(name, safe=''))
                with urlopen(url, timeout=60) as response, (source / name).open('wb') as output:
                    shutil.copyfileobj(response, output)
        # Reuse the official asset checks and actual Linux execution gate. No
        # network transport or command registry is reimplemented here.
        assets = work / 'assets'
        prepare(DEFAULT_LOCK, source, assets)
        candidate = work / 'dart-control'
        shutil.copytree(ROOT / 'skills/dart-control', candidate)
        (candidate / 'bin').mkdir()
        shutil.copy2(assets / 'dart-cli-linux-x64', candidate / 'bin/dart')
        for name in ('dart-cli-reference.md', 'dart-cli-command-catalog.json', 'dart-agent-distribution.json'):
            shutil.copy2(assets / name, candidate / 'references' / name)
        (candidate / 'installation.json').write_text(json.dumps(dict(
            skillVersion=lock['skillVersion'], dartVersion=lock['dartVersion'],
            source='local-release-assets' if asset_dir else ('development-prepared-assets' if prepared_dir else 'github-release'),
            release='kalstein00/dart-agent@v' + lock['skillVersion'])) + '\n')
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
    parser.add_argument('--update', action='store_true', help='explicitly replace managed skill files, preserving official profiles')
    args = parser.parse_args()
    try:
        target = install(args.skills_dir.expanduser().absolute(), args.prepared_dir, args.update, args.asset_dir)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, URLError) as error:
        print(f'installation failed: {error}', file=sys.stderr)
        return 1
    print(json.dumps(dict(ok=True, skill=str(target), source='local-release-assets' if args.asset_dir else ('development-prepared-assets' if args.prepared_dir else 'github-release'))))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
