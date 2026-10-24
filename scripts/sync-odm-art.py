#!/usr/bin/env python3
"""Hash-audit ODM image directories against this library; optionally import missing bytes."""
import argparse
from collections import Counter
from datetime import date
import hashlib
import io
import json
from pathlib import Path
import shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EXTENSIONS = {'.png', '.webp', '.jpg', '.jpeg', '.svg'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, action='append', required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    index_path = ROOT / 'art-index.json'
    index = json.loads(index_path.read_text())
    known = {}
    for p in (ROOT / 'public/assets').rglob('*'):
        if p.is_file() and p.suffix.lower() in EXTENSIONS:
            known[hashlib.sha256(p.read_bytes()).hexdigest()] = p.relative_to(ROOT).as_posix()
    rows, rejected, imported = [], [], []
    for number, source in enumerate(args.source):
        if not source.is_dir():
            raise ValueError(f'Missing source directory: {source}')
        for p in sorted(source.rglob('*')):
            if not p.is_file() or p.is_symlink() or p.suffix.lower() not in EXTENSIONS:
                continue
            data = p.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            row = {'source': number, 'name': p.relative_to(source).as_posix() if number == 0 else sha + p.suffix.lower(), 'bytes': len(data), 'sha256': sha}
            if sha in known:
                rows.append({**row, 'path': known[sha], 'status': 'present'})
                continue
            # Preserve all source vectors too; images[] stays a raster-only registry.
            vector = p.suffix.lower() == '.svg'
            try:
                if vector:
                    import xml.etree.ElementTree as ET
                    if ET.fromstring(data).tag.split('}')[-1] != 'svg':
                        raise ValueError('Not SVG')
                else:
                    with Image.open(io.BytesIO(data)) as image:
                        image.load()
                        width, height = image.size
                        mime = Image.MIME[image.format]
            except Exception as error:
                rejected.append({**row, 'reason': type(error).__name__})
                continue
            dest = f'public/assets/imported/odm/{sha}{p.suffix.lower()}'
            rows.append({**row, 'path': dest, 'status': 'imported' if args.apply else 'missing'})
            known[sha] = dest
            if not args.apply:
                continue
            target = ROOT / dest
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, target)
            assert hashlib.sha256(target.read_bytes()).hexdigest() == sha
            imported.append(dest)
            if vector:
                continue
            index['images'].append({'category': 'resource', 'subjectId': 'odm-' + sha[:20],
                'name': 'ODM artwork resource', 'variantId': '01', 'style': 'normal',
                'path': dest, 'mime': mime, 'width': width, 'height': height,
                'bytes': len(data), 'sha256': sha,
                'provenance': {'sourceType': 'existing-odm-resource', 'importedAt': date.today().isoformat(),
                    'bytesUnchanged': True, 'license': 'Original source attribution retained in ODM; no new license asserted'}})
    if args.apply:
        index['imageCount'] = len(index['images'])
        index['imageBytes'] = sum(entry['bytes'] for entry in index['images'])
        for category, count in Counter(entry['category'] for entry in index['images']).items():
            index[category + 'ImageCount'] = count
        index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    report = {'date': date.today().isoformat(), 'sources': len(args.source), 'checked': len(rows) + len(rejected),
        'uniqueImported': len(imported), 'counts': dict(Counter(row['status'] for row in rows)),
        'rows': rows, 'rejected': rejected}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ['checked', 'uniqueImported', 'counts']}))
    print('Rejected non-images:', len(rejected))


if __name__ == '__main__':
    main()
