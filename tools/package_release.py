"""Package the pinned Release assets into one ZIP."""
import argparse
from pathlib import Path
import zipfile

from prepare_release import DEFAULT_LOCK, load, safe_name, verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    records = load(DEFAULT_LOCK)['assets']
    # Verify every input before creating an archive.
    for record in records:
        verify((args.source_dir / safe_name(record['file'])).read_bytes(), record)
    with zipfile.ZipFile(args.output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for record in records:
            name = safe_name(record['file'])
            archive.write(args.source_dir / name, name)


if __name__ == '__main__':
    main()
