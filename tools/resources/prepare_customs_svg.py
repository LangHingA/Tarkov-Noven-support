"""Pinned five-floor Customs candidate; local NVR1 only, independent geometry pending."""
import argparse
import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from package_map import package, reject_reparse, safe_name
from prepare_additional_svg import REF, SHEBUKA_REF, convert, inspect_svg, png, rows, sha, tile_pack

MAP_ID = '56f40101d2720b2a4d8b45d6'
BASE_URL = f'https://raw.githubusercontent.com/acidphantasm/SPT-DynamicMaps/{REF}/Plugin/Resources/Maps/Customs_TarkovDev/'
FLOORS = {
    'Ground_Level': 'Ground_Level', 'Second_Floor': 'Second_Floor',
    'Third_Floor': 'Third_Floor', '4th_Floor': 'Fourth_Floor',
    'Underground_Level': 'Underground_Level',
}
PINS = {
    'Customs-Ground_Level.svg': ('Layers/Customs-Ground_Level.svg', '5be31c29173854f5f832c3fea072bfd8603e27eeca2052754f3798cbf1b6b6d9'),
    'Customs-Second_Floor.svg': ('Layers/Customs-Second_Floor.svg', '3bb882642f6288b651a7e3a1939bb9f379b8a81de679630fd0259499f7e73e64'),
    'Customs-Third_Floor.svg': ('Layers/Customs-Third_Floor.svg', '7a5626c748ee4fb45c5b9e9e451691e1811b25ee103da4fc1a1c5b8a3fb4d203'),
    'Customs-Fourth_Floor.svg': ('Layers/Customs-Fourth_Floor.svg', 'd4bd72d8fd9f5e7f8e7c64f6848863b87c425843aaf058a78d6f256a9dc6cba0'),
    'Customs-Underground_Level.svg': ('Layers/Customs-Underground_Level.svg', '9d5fe0a3c0bec91dd38fbf045a71548ac5d33df1c46dab4e81ff73931da8567c'),
    'Customs.svg': ('Layers/SVG/Customs.svg', '40c33a8ac0813af73bad7c5c3c9f3a0c7fc36f9b6e401bf68834b982b2630fe4'),
    'Customs.jsonc': ('Customs_TarkovDev.jsonc', '6924222ceb18c4752cc8fd17d0a234765b597d3c140a805144e623efcb4206be'),
    'LICENSE.md': ('Layers/Shebuka-LICENSE-MODIFIED BY ACIDPHANTASM.md', '1349a4b6148492b44f629e64eed676612e234fe9a839e4f3b277c1482c8849f1'),
    'README.md': (f'https://raw.githubusercontent.com/the-hideout/tarkov-dev-svg-maps/{SHEBUKA_REF}/README.md', 'ee4022e968c052d2920251ba2181b5ebd9ffb45c5c69bdea916bd9f3a6e7031a'),
}


def source_url(name):
    path = PINS[name][0]
    return path if path.startswith('https://') else BASE_URL + path.replace(' ', '%20')


def verify_source(name, raw):
    if hashlib.sha256(raw).hexdigest() != PINS[name][1]:
        raise ValueError('pinned source hash mismatch: ' + name)
    if name.endswith('.svg'):
        inspect_svg(raw)
    return raw


def contract(assets):
    floor_sets = []
    references = []
    for prefix in ('', 'pve/'):
        floors = [r for r in rows(assets, prefix + 'map_floors.tsv') if r['mapId'] == MAP_ID]
        if len(floors) != len(FLOORS) or {r['floorId'] for r in floors} != set(FLOORS):
            raise ValueError('native five-floor contract changed')
        if any(not safe_name(r[k]) or not r[k].endswith('.png')
               or not r[k].startswith('maps/customs/') for r in floors for k in ('abstractPath', 'satellitePath')):
            raise ValueError('unsafe native image path')
        floor_sets.append(floors)
        references.append(next(r for r in rows(assets, prefix + 'map_references.tsv') if r['mapId'] == MAP_ID))
        fourth = [r for r in rows(assets, prefix + 'map_extents.tsv')
                  if r['mapId'] == MAP_ID and r['floorId'] == '4th_Floor']
        if len(fourth) != 1 or [float(fourth[0][k]) for k in ('bottom', 'top', 'minX', 'maxX', 'minZ', 'maxZ')] != [11.2, 54.7, 246, 279, -79, -1.4]:
            raise ValueError('native fourth-floor region changed')
    target = references[0]
    if references[1] != target or floor_sets[0] != floor_sets[1]:
        raise ValueError('PvP/PvE floor or projection contract differs')
    if [float(target[k]) for k in ('width', 'height', 'rotation', 'minX', 'maxX', 'minZ', 'maxZ')] != [1070, 544, 180, -372, 698, -307, 237]:
        raise ValueError('native Customs projection changed')
    return target, floor_sets[0]


def fourth_correspondence(raw, source, target):
    root = inspect_svg(raw)
    group = next(g for g in root if g.get('id') == 'Fourth_Floor')
    counts = {tag: sum(n.tag.endswith('}' + tag) for n in group) for tag in ('path', 'rect', 'polygon')}
    if counts != dict(path=2, rect=2, polygon=1):
        raise ValueError('fourth-floor physical primitives changed')
    boxes = []
    # 只验证来源标定下的两块实体轮廓；这不是独立测量或控制点验收。
    # Check physical outlines under source calibration, not independent survey/control points.
    for index in range(2):
        copy = ET.fromstring(raw)
        selected = next(g for g in copy if g.get('id') == 'Fourth_Floor')
        paths = [n for n in selected if n.tag.endswith('}path')]
        for n in list(selected):
            if n is not paths[index]:
                selected.remove(n)
        image = convert(ET.tostring(copy), source, target, None, (4280, 2176))
        left, top, right, bottom = image.getchannel('A').getbbox()
        box = [698 - right / 4, -307 + top / 4, 698 - left / 4, -307 + bottom / 4]
        if not (244 <= box[0] < box[2] <= 280 and -81 <= box[1] < box[3] <= 0):
            raise ValueError('fourth-floor outline outside oilrig/panda region')
        boxes.append(box)
    return dict(method='alpha bounds at 4 pixels/world unit; source metadata calibration only',
                outlineWorldBounds=boxes, primitiveCounts=counts,
                nativeRegion=dict(minX=246, maxX=279, minZ=-79, maxZ=-1.4, bottom=11.2, top=54.7),
                independentGeometryVerified=False)


def prepare(assets, output, version, upstream=None):
    for directory in (assets, upstream, output.parent):
        if directory is not None:
            for parent in (directory.absolute(), *directory.absolute().parents):
                if parent.exists():
                    reject_reparse(parent)
    if output.exists():
        raise ValueError('fresh output directory required')
    target, floors = contract(assets)
    inputs = {}
    for name in PINS:
        if upstream is None:
            request = urllib.request.Request(source_url(name), headers={'User-Agent': 'Noven-Customs-candidate/1.0'})
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read(1024 * 1024)
        else:
            reject_reparse(upstream / name)
            raw = (upstream / name).read_bytes()
        inputs[name] = verify_source(name, raw)
    config = json.loads(inputs['Customs.jsonc'].decode('utf-8-sig').split('"DefaultLevel"')[0].rstrip().rstrip(',') + '}')
    source = {**config['Bounds'], 'rotation': config['CoordinateRotation']}
    report = dict(mapId=MAP_ID, status='candidate: independent geometry review pending', publishable=False,
                  assetLicense='CC BY-NC-SA 4.0; asset-specific notice verified',
                  attribution='Shebuka; supplied modifications by acidphantasm', revision=REF,
                  sourceBounds=source, nativeReference=target,
                  fourthFloor=fourth_correspondence(inputs['Customs-Fourth_Floor.svg'], source, target),
                  nativeRuntimeValidation='pending main isolated --local-package compatibility check',
                  calibrationMetadata=dict(url=source_url('Customs.jsonc'), sha256=PINS['Customs.jsonc'][1],
                                           distribution='original JSONC retained locally in upstream only; no artwork-license grant asserted for metadata'),
                  sourcePins={n: dict(url=source_url(n), sha256=PINS[n][1]) for n in PINS}, floors={})
    output.mkdir(parents=True, exist_ok=False)
    archive = output / 'upstream'
    archive.mkdir()
    for name, raw in inputs.items():
        (archive / name).write_bytes(raw)
    root = output / 'input'
    inventory = dict(classification='approved', approvalReference=source_url('LICENSE.md') +
                     '; local asset redistribution eligibility only; independent geometry NOT approved', files={})

    def add(relative, raw, url, creator):
        if not safe_name(relative):
            raise ValueError('unsafe package destination')
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        inventory['files'][relative] = dict(source=url, creator=creator, license='CC BY-NC-SA 4.0', sha256=sha(path))

    for row in floors:
        floor = row['floorId']
        filename = 'Customs-' + FLOORS[floor] + '.svg'
        raw = inputs[filename]
        groups = {g.get('id') for g in inspect_svg(raw) if g.tag.endswith('}g')}
        if groups != ({'Ground_Level', 'First_Floor'} if floor == 'Ground_Level' else {FLOORS[floor]}):
            raise ValueError('unexpected standalone floor groups')
        # 地面文件含首层伴随组；保留两组，其他楼层只使用各自的新来源。
        # Ground includes its first-floor companion; every other floor uses its own new source.
        image = convert(raw, source, target, None, (4096, round(4096 * 544 / 1070)))
        preview = png(image.resize((1024, round(1024 * 544 / 1070))))
        tiles = tile_pack(png(image))
        for path in sorted({row['abstractPath'], row['satellitePath']}):
            add(path, preview, source_url(filename), report['attribution'])
            add(str(Path(path).with_suffix('.tiles')).replace('\\', '/'), tiles, source_url(filename), report['attribution'])
        prefix = f'maps/customs/sources/{floor}/'
        add(prefix + 'SOURCE.svg', raw, source_url(filename), report['attribution'])
        add(prefix + 'LICENSE.txt', inputs['LICENSE.md'], source_url('LICENSE.md'), 'Creative Commons license text')
        add(prefix + 'UPSTREAM-README.md', inputs['README.md'], source_url('README.md'), 'tarkov-dev-svg-maps notice authors')
        notice = (f'# Customs {floor} - CANDIDATE ONLY\n\nArtwork: Shebuka; supplied modifications by acidphantasm.\n'
                  f'Source: {source_url(filename)}\nSHA-256: {PINS[filename][1]}\n'
                  f'Calibration metadata reference only: {source_url("Customs.jsonc")}\nSHA-256: {PINS["Customs.jsonc"][1]}\n'
                  'Original JSONC is not included in this package; its metadata license is not inferred from the artwork license.\n'
                  f'Supplied modified-asset notice: {source_url("LICENSE.md")}\n'
                  'CC BY-NC-SA 4.0 https://creativecommons.org/licenses/by-nc-sa/4.0/; full LICENSE.txt and upstream additional anti-cheating statement preserved.\n\n'
                  'Noven changes: affine mapping to unchanged native projection, PNG previews and NVTILES1 tiling. '
                  'Both native image modes contain newly rendered vectors; no inherited images or satellite imagery. '
                  'Original SVG bytes retained unchanged. Noven copyrightable adaptations use CC BY-NC-SA 4.0. '
                  'Actual use noncommercial, official features free, cheating prohibited; no endorsement.\n\n'
                  'Independent geometry review pending. License and rendering checks do not establish current-game accuracy.\n')
        add(prefix + 'SOURCE.md', notice.encode(), source_url(filename), 'Noven conversion and attribution record')
        report['floors'][floor] = dict(sourceGroup=FLOORS[floor], retainedGroups=sorted(groups),
                                     detailSize=list(image.size), alphaBounds=image.getchannel('A').getbbox(),
                                     nativePaths=sorted({row['abstractPath'], row['satellitePath']}), inheritedImages=False)
    add('maps/customs/SOURCE.svg', inputs['Customs.svg'], source_url('Customs.svg'), report['attribution'])
    add('maps/customs/LICENSE.txt', inputs['LICENSE.md'], source_url('LICENSE.md'), 'Creative Commons license text')
    add('maps/customs/PROVENANCE.json', json.dumps(report, sort_keys=True, indent=2).encode(), source_url('Customs.svg'), 'Noven candidate evidence record')
    inventory_path = output / 'inventory.json'
    inventory_path.write_text(json.dumps(inventory, sort_keys=True, indent=2), encoding='utf-8')
    record = package(root, inventory_path, output / 'package', MAP_ID, version, '海关 SVG 候选', 'Customs SVG candidate')
    report['package'] = record
    report['totalOutputBytesBeforeReport'] = sum(p.stat().st_size for p in output.rglob('*') if p.is_file())
    (output / 'candidate-report.json').write_text(json.dumps(report, sort_keys=True, indent=2), encoding='utf-8')
    if sum(p.stat().st_size for p in output.rglob('*') if p.is_file()) > 30 * 1024 * 1024:
        raise ValueError('candidate exceeds 30 MiB; retained for review, no deletion')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--version', default='0.0.1')
    parser.add_argument('--upstream', type=Path, help='Offline pinned inputs; omitted: download fixed revisions')
    args = parser.parse_args()
    result = prepare(args.assets, args.output, args.version, args.upstream)
    print(json.dumps(dict(status=result['status'], package=result['package'], fourthFloor=result['fourthFloor'])))
