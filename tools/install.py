"""Install the pinned DART control skill from dart-agent Release attachments."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from prepare_release import DEFAULT_LOCK, load, prepare, require

ROOT = Path(__file__).resolve().parents[1]


def install(skills_dir, prepared_dir=None, update=False):
    lock = load(DEFAULT_LOCK)
    target = skills_dir / 'dart-control'
    require(not target.exists() or update, 'already installed; use --update explicitly')
    skills_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.dart-install-', dir=skills_dir) as temporary:
        work = Path(temporary)
        source = prepared_dir
        if source is None:
            source = work / 'download'
            source.mkdir()
            subprocess.run(['gh', 'release', 'download', 'v' + lock['skillVersion'],
                            '--repo', 'kalstein00/dart-agent', '--dir', str(source),
                            *[arg for row in lock['assets'] for arg in ('--pattern', row['file'])]],
                           check=True, timeout=600, capture_output=True)
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
            source='development-prepared-assets' if prepared_dir else 'github-release',
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
    parser.add_argument('--prepared-dir', type=Path, help='development only: verified preparation output, not Release proof')
    parser.add_argument('--update', action='store_true', help='explicitly replace managed skill files, preserving official profiles')
    args = parser.parse_args()
    try:
        target = install(args.skills_dir.expanduser().absolute(), args.prepared_dir, args.update)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(f'installation failed: {error}', file=sys.stderr)
        return 1
    print(json.dumps(dict(ok=True, skill=str(target), source='development-prepared-assets' if args.prepared_dir else 'github-release')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
