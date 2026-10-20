"""Read-only floor/package inventory. This does NOT certify geometry or signatures.

Run the native authenticated catalog verifier separately. Inputs are explicit;
there is no network, extraction, activation, deletion or publication here.
"""
import argparse
import csv
import hashlib
import json
import re
import struct
from pathlib import Path
from package_map import safe_name


def rows(assets, name):
    with (assets / 'data' / name).open(encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def package_inventory(path, record):
    if path.stat().st_size != record['downloadSize'] or digest(path) != record['sha256']:
        raise ValueError('package identity mismatch')
    entries, installed, provenance, source_hash = {}, 0, {}, None
    with path.open('rb') as stream:
        def take(size):
            data = stream.read(size)
            if len(data) != size:
                raise ValueError('truncated package')
            return data
        if take(4) != b'NVR1':
            raise ValueError('not NVR1')
        length, = struct.unpack('<I', take(4))
        if not 0 < length <= 69 or take(length).decode('ascii') != record['resourceId']:
            raise ValueError('resource identity mismatch')
        count, = struct.unpack('<I', take(4))
        if not 0 < count <= 30000:
            raise ValueError('entry count bound')
        for _ in range(count):
            length, size = struct.unpack('<IQ', take(12))
            if not 0 < length <= 240 or not 0 < size <= 512 * 1024 ** 2:
                raise ValueError('entry bound')
            name = take(length).decode('ascii')
            if not safe_name(name) or name.lower() in entries:
                raise ValueError('unsafe/duplicate entry')
            entries[name.lower()] = size
            installed += size
            if installed > 8 * 1024 ** 3 or stream.tell() + size > path.stat().st_size:
                raise ValueError('truncated/oversized content')
            if name.endswith('/PROVENANCE.json'):
                if size > 2 * 1024 ** 2:
                    raise ValueError('provenance bound')
                provenance = json.loads(take(size))
            elif name.endswith('/SOURCE.svg'):
                hasher = hashlib.sha256()
                remaining = size
                while remaining:
                    block = take(min(remaining, 65536))
                    hasher.update(block)
                    remaining -= len(block)
                source_hash = hasher.hexdigest()
            else:
                stream.seek(size, 1)
        if stream.read(1) or installed != record['installedSize']:
            raise ValueError('trailing content/installed size mismatch')
    return entries, provenance, source_hash


def floor_status(floor, reference, abstract, entries):
    preview = floor['abstractPath'].lower()
    detail = str(Path(preview).with_suffix('.tiles')).replace('\\', '/')
    packaged = bool(entries) and preview in entries and detail in entries
    return dict(floorId=floor['floorId'], order=int(floor['order']),
                nameEn=floor['nameEn'], nameZh=floor['nameZh'],
                sourceKind=abstract.get('kind', 'unknown'),
                preview=preview, detail=detail, packagedPreview=preview in entries,
                packagedDetail=detail in entries, packageCoverage=packaged,
                coordinateReference='map_references.tsv' if reference else 'missing',
                geometricSurvey='not independently measured by this inventory')


def audit(assets, catalog, packages):
    envelope = json.loads(catalog.read_bytes())
    payload = json.loads(bytes.fromhex(envelope['payloadHex']))
    if payload['schemaVersion'] != 1 or payload['audience'] != 'production':
        raise ValueError('wrong catalog domain/schema')
    maps = rows(assets, 'map_maps.tsv')
    ids = {r['id'] for r in maps}
    records = {}
    for record in payload['components']:
        identity = record['stableMapId']
        if identity not in ids or identity in records or record['resourceId'] != 'maps.' + identity:
            raise ValueError('unknown/duplicate/spoofed resource')
        if not re.fullmatch(r'[a-z0-9.-]+\.nvr', record['artifact']) or '/' in record['artifact']:
            raise ValueError('unsafe artifact')
        records[identity] = record
    floors = rows(assets, 'map_floors.tsv')
    if floors != rows(assets, 'pve/map_floors.tsv'):
        raise ValueError('regular/PvE floor contracts differ')
    references = {r['mapId']: r for r in rows(assets, 'map_references.tsv')}
    extents = rows(assets, 'map_extents.tsv')
    ledger = json.loads((assets / 'maps/all.manifest.json').read_bytes())
    sources = {r['url']: r.get('sha256') for r in ledger['sources']}
    results = []
    for item in maps:
        identity = item['id']
        record = records.get(identity)
        entries, provenance, source_hash = package_inventory(packages / record['artifact'], record) if record else ({}, {}, None)
        projection = references.get(identity)
        floor_results = []
        for floor in (f for f in floors if f['mapId'] == identity):
            stem = floor['abstractPath'].removesuffix('.png').removesuffix('.satellite')
            meta = assets / (stem + '.manifest.json')
            metadata = json.loads(meta.read_bytes()) if meta.is_file() else {}
            abstract = metadata.get('abstract') or {}
            raster_urls = (metadata.get('satellite') or {}).get('sourceUrls', [])
            result = floor_status(floor, projection, abstract, entries)
            result['heightRegions'] = [{k: v for k, v in r.items() if k not in ('mapId', 'floorId')}
                                       for r in extents if r['mapId'] == identity and r['floorId'] == floor['floorId']]
            result['developmentPreviewPresent'] = (assets / floor['abstractPath']).is_file()
            result['developmentDetailPresent'] = (assets / result['detail']).is_file()
            result['source'] = provenance.get('source') or abstract.get('source')
            if not record and not result['source'] and raster_urls:
                result['source'] = raster_urls[0]
                result['sourceIsRasterSample'] = True
                result['rasterSourceCount'] = len(raster_urls)
            result['sourceSha256'] = source_hash if record else sources.get(result['source'])
            result['license'] = provenance.get('license') or (abstract.get('rights', {}).get('declaredLicense') if abstract.get('kind') == 'svg' else None)
            result['sourceRevision'] = provenance.get('calibrationRevision') if provenance.get('source') else None
            result['revisionEvidence'] = 'pinned source in package' if result['sourceRevision'] else 'content hash only; no exact game-layout revision established'
            if record and result['source'] is None:
                original = next((v for k, v in provenance.get('files', {}).items() if k.endswith('/SOURCE.svg')), {})
                result['source'] = original.get('source')
                result['license'] = original.get('license')
            if record:
                result['sourceKind'] = 'svg-derived production package'
            floor_results.append(result)
        # 空楼层不是“全部通过”；文件齐全也不等于几何实测通过。
        # Empty floors never pass vacuously; file coverage is not geometric accuracy.
        complete = bool(projection and floor_results) and all(f['packageCoverage'] for f in floor_results)
        if record and not complete:
            raise ValueError('published package does not cover the native floor contract: ' + identity)
        results.append(dict(mapId=identity, resourceId='maps.' + identity, nameEn=item['nameEn'],
                            nameZh=item['nameZh'], projection=projection, published=bool(record),
                            package=record, packageFloorCoverage=complete,
                            nativeContractBlocker=None if projection and floor_results else 'missing projection/floors; resource-only delivery cannot supply Core TSVs',
                            geometryVerdict='not certified by inventory', floors=floor_results))
    return dict(schemaVersion=1, applicationVersion='0.1.3',
                catalogPayloadSha256=hashlib.sha256(bytes.fromhex(envelope['payloadHex'])).hexdigest(),
                signatureVerification='external native verifier required; this tool is not a trust authority',
                mapCount=len(maps), floorCount=len(floors), publishedCount=len(records), maps=results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('assets', 'catalog', 'packages'):
        parser.add_argument('--' + flag, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.assets, args.catalog, args.packages), ensure_ascii=False, indent=2))
