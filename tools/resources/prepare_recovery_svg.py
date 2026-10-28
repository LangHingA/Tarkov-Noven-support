"""Local-only Reserve/Lab candidates. No publication or geometry certification.

Reserve intentionally has NO package while four native floors are missing.
Lab may produce an unsigned candidate NVR1, never a production catalog.
"""
import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

from package_map import package, reject_reparse, safe_name
from prepare_additional_svg import CASES, REF, SHEBUKA_REF, convert, inspect_svg, png, rows, tile_pack

MAX_OUTPUT = 16 * 1024 * 1024
BASE = f'https://raw.githubusercontent.com/acidphantasm/SPT-DynamicMaps/{REF}/Plugin/Resources/Maps/Reserve_TarkovData/'
RESERVE = '5704e5fad2720bc05b8b4567'
LAB = '5b0fc42d86f7744a585f9105'
NOTICE_HASH = '1349a4b6148492b44f629e64eed676612e234fe9a839e4f3b277c1482c8849f1'
README_HASH = 'ee4022e968c052d2920251ba2181b5ebd9ffb45c5c69bdea916bd9f3a6e7031a'
README_URL = f'https://raw.githubusercontent.com/the-hideout/tarkov-dev-svg-maps/{SHEBUKA_REF}/README.md'


def sources(map_id):
    if map_id == RESERVE:
        return {
            'Ground.svg': (BASE + 'Layers/Reserve-Ground_Level.svg', '804dec62ad3ec4dc74f6bbb973c342165e9c373750be275b22ff3c60151a9d94'),
            'Bunkers.svg': (BASE + 'Layers/Reserve-Bunkers.svg', '2436a8e2662016383f56ed14b5eb9f7f0c5fcc91352733a8db4eb5bec546806b'),
            'config.jsonc': (BASE + 'Reserve_TarkovData.jsonc', 'a68466f405add8c7d3ad8c1e757457fbc556ad80741163e5cb2eac14c630c5d0'),
            'LICENSE.txt': (BASE + 'Layers/Shebuka-LICENSE.md', NOTICE_HASH),
            'README.md': (README_URL, README_HASH),
        }
    if map_id == LAB:
        case = CASES[0]
        return {
            'SOURCE.svg': (case['url'], case['sha']),
            'config.jsonc': (f'https://raw.githubusercontent.com/acidphantasm/SPT-DynamicMaps/{REF}/Plugin/Resources/Maps/Labs_TarkovDev/Labs_TarkovDev.jsonc', case['configSha']),
            'LICENSE.txt': (f'https://raw.githubusercontent.com/the-hideout/tarkov-dev-svg-maps/{SHEBUKA_REF}/LICENSE.md', NOTICE_HASH),
            'README.md': (README_URL, README_HASH),
        }
    raise ValueError('unsupported recovery identity')


def load_inputs(map_id, upstream):
    result = {}
    for name, (url, expected) in sources(map_id).items():
        if upstream is None:
            with urllib.request.urlopen(url, timeout=25) as stream:
                raw = stream.read(1024 * 1024 + 1)
        else:
            path = upstream.absolute() / name
            for ancestor in (path, *path.parents):
                reject_reparse(ancestor)
            if path.stat().st_size > 1024 * 1024:
                raise ValueError('source bound')
            raw = path.read_bytes()
        if len(raw) > 1024 * 1024 or hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('source bound/hash mismatch: ' + name)
        if name.endswith('.svg'):
            inspect_svg(raw)
        result[name] = raw
    return result


def prepare(assets, map_id, output, upstream=None):
    pins = sources(map_id)
    if output.exists():
        raise ValueError('output must be NEW; preserve existing candidates')
    for ancestor in (output.absolute().parent, *output.absolute().parent.parents):
        if ancestor.exists():
            reject_reparse(ancestor)
    floors = [r for r in rows(assets, 'map_floors.tsv') if r['mapId'] == map_id]
    pve = [r for r in rows(assets, 'pve/map_floors.tsv') if r['mapId'] == map_id]
    target = next(r for r in rows(assets, 'map_references.tsv') if r['mapId'] == map_id)
    pve_target = next(r for r in rows(assets, 'pve/map_references.tsv') if r['mapId'] == map_id)
    expected = {'Ground_Level', '2nd_Floor', '3rd_Floor', '4th_Floor', '5th_Floor', 'Bunkers'} if map_id == RESERVE else set(CASES[0]['floors'])
    if floors != pve or target != pve_target or {f['floorId'] for f in floors} != expected or len(floors) != len(expected):
        raise ValueError('native PvP/PvE floor/projection contract differs')
    inputs = load_inputs(map_id, upstream)
    config = json.loads(inputs['config.jsonc'].decode('utf-8-sig').split('"StaticMarkers"')[0].rstrip().rstrip(',') + '}')
    source = {**config['Bounds'], 'rotation': config['CoordinateRotation']}
    selection = {'Ground_Level': ('Ground.svg', None), 'Bunkers': ('Bunkers.svg', None)} if map_id == RESERVE else {
        f: ('SOURCE.svg', group) for f, group in CASES[0]['floors'].items()}
    slug = target['slug']
    size = (4096, round(4096 * float(target['height']) / float(target['width'])))
    report = dict(schemaVersion=1, mapId=map_id, status='BLOCKED', publishable=False,
                  independentGeometryVerified=False, heldOutRmse=None, heldOutMaximum=None,
                  missingFloors=sorted(expected - selection.keys()), nativeReference=target,
                  sourceCalibration=source, sources={n: dict(url=u, sha256=h) for n, (u, h) in pins.items()}, floors={})
    files, inventory = {}, dict(classification='approved', approvalReference=pins['LICENSE.txt'][0] + '; artwork grant only, geometry NOT accepted', files={})

    def add(name, data, source_name):
        if not safe_name(name) or name in files:
            raise ValueError('unsafe/duplicate destination')
        files[name] = data
        creator = 'Creative Commons license text' if source_name == 'LICENSE.txt' else 'tarkov-dev-svg-maps notice authors' if source_name == 'README.md' else 'Shebuka'
        inventory['files'][name] = dict(source=pins[source_name][0], creator=creator,
                                       license='CC BY-NC-SA 4.0', sha256=hashlib.sha256(data).hexdigest())

    for floor in floors:
        floor_id = floor['floorId']
        if floor_id not in selection:
            continue
        name, group = selection[floor_id]
        root = inspect_svg(inputs[name])
        groups = {g.get('id') for g in root if g.tag.endswith('}g')}
        if map_id == RESERVE and groups != {floor_id}:
            raise ValueError('unexpected standalone Reserve groups')
        image = convert(inputs[name], source, target, group, size)
        preview = png(image.resize((1024, round(1024 * size[1] / size[0]))))
        tiles = tile_pack(png(image))
        native_paths = sorted({floor['abstractPath'], floor['satellitePath']} - {''})
        for path in native_paths:
            if not path.startswith('maps/' + slug + '/'):
                raise ValueError('native path outside map')
            add(path, preview, name)
            add(Path(path).with_suffix('.tiles').as_posix(), tiles, name)
        prefix = f'maps/{slug}/sources/{floor_id}/'
        add(prefix + 'SOURCE.svg', inputs[name], name)
        add(prefix + 'LICENSE.txt', inputs['LICENSE.txt'], 'LICENSE.txt')
        add(prefix + 'UPSTREAM-README.md', inputs['README.md'], 'README.md')
        notice = (f'# {slug} {floor_id}: LOCAL CANDIDATE ONLY\n\nAuthor: {inventory["files"][prefix + "SOURCE.svg"]["creator"]}.\n'
                  f'Original source: {pins[name][0]}\nSHA-256: {pins[name][1]}\n'
                  f'Asset license: {pins["LICENSE.txt"][0]}\n'
                  'CC BY-NC-SA 4.0 https://creativecommons.org/licenses/by-nc-sa/4.0/; full license and upstream anti-cheating statement retained.\n'
                  f'Calibration metadata reference: {pins["config.jsonc"][0]}\nSHA-256: {pins["config.jsonc"][1]}\n'
                  'JSONC is not distributed under an invented artwork license.\n\n'
                  'Split-layer distribution, where applicable: SPT-DynamicMaps (acidphantasm). '
                  'Noven modifications: source-floor selection, affine conversion to unchanged native projection, PNG previews and NVTILES1 detail tiles. '
                  'Original SVG unchanged. Adaptations: CC BY-NC-SA 4.0. Actual use noncommercial, official features free, cheating prohibited. No endorsement. '
                  'No satellite imagery, screenshots or game icons. Independent image/world geometry NOT validated; do not publish.\n')
        add(prefix + 'SOURCE.md', notice.encode(), name)
        report['floors'][floor_id] = dict(source=name, group=group, nativePaths=native_paths, detailSize=list(size),
                                         alphaBounds=list(image.getchannel('A').getbbox()), previewSha256=hashlib.sha256(preview).hexdigest(),
                                         detailSha256=hashlib.sha256(tiles).hexdigest())
    add(f'maps/{slug}/PROVENANCE.json', json.dumps(report, sort_keys=True, indent=2).encode(), next(n for n in pins if n.endswith('.svg')))
    # 先计算总量再落盘；缺失楼层绝不补占位或封成“完整”资源包。
    # Bound output before writing; missing floors never get placeholders or a complete-map package.
    total = sum(map(len, files.values())) + sum(map(len, inputs.values()))
    if total * 2 + 128 * 1024 > MAX_OUTPUT:
        raise ValueError('candidate output budget exceeded before writing')
    output.mkdir(parents=True, exist_ok=False)
    for name, raw in inputs.items():
        path = output / 'upstream' / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(raw)
    for name, raw in files.items():
        path = output / 'input' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    inv = output / 'inventory.json'
    inv.write_text(json.dumps(inventory, sort_keys=True, indent=2), encoding='utf-8')
    if not report['missingFloors']:
        report['package'] = package(output / 'input', inv, output / 'package', map_id, '0.0.1', 'SVG 本地候选', 'SVG local candidate')
    (output / 'candidate-report.json').write_text(json.dumps(report, sort_keys=True, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', type=Path, required=True)
    parser.add_argument('--map-id', choices=(RESERVE, LAB), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--upstream', type=Path, help='Offline pinned inputs using filenames from sources(); default fetches fixed revisions')
    args = parser.parse_args()
    report = prepare(args.assets, args.map_id, args.output, args.upstream)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
