"""Create local Customs/Lab image observations, never invent matching world points.

The selected SVG vertices are acquisition targets, NOT identified physical
landmarks. The fixed fit/holdout split is provisional until identities are
independently reviewed, before any world coordinates are fitted.
"""
import argparse
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from calibrate_map_geometry import calibrate, compose, inverse, markdown, projection, residual_svg
from package_map import reject_reparse
from prepare_additional_svg import CASES, inspect_svg, raster_svg, rows
from prepare_customs_svg import FLOORS, MAP_ID, PINS, source_url, verify_source
from prepare_recovery_svg import LAB, load_inputs, sources

FLOAT = r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?'


def vertices(node, location='', transformed=False):
    """Only directly observable vertices; skip transformed ancestry, never guess it."""
    transformed = transformed or bool(node.get('transform'))
    tag = node.tag.split('}')[-1]
    location += '/' + node.get('id', tag)
    if not transformed:
        if tag == 'polygon':
            values = [float(x) for x in re.findall(FLOAT, node.get('points', ''))]
            if len(values) % 2:
                raise ValueError('odd polygon coordinates')
            for index in range(0, len(values), 2):
                yield location+f'/vertex[{index//2+1}]', values[index:index+2]
        if tag == 'path':
            match = re.match(r'\s*[Mm]\s*('+FLOAT+r')[\s,]*('+FLOAT+r')', node.get('d', ''))
            if match:
                yield location+'/initial-moveto', [float(match[1]), float(match[2])]
    for index, child in enumerate(node):
        yield from vertices(child, location+f'/child[{index+1}]', transformed)


def select_observations(root, group, view):
    target = next(n for n in root if n.get('id') == group)
    candidates = []
    seen = set()
    vx, vy, width, height = view
    for locator, uv in vertices(target):
        if tuple(uv) not in seen and vx <= uv[0] <= vx+width and vy <= uv[1] <= vy+height:
            candidates.append((locator, uv)); seen.add(tuple(uv))
    if not candidates:
        raise ValueError('no directly observable vertices')
    # 最远点只用于分散采集目标，不将空间分散伪装成实体对应证明。
    # Farthest-point sampling spreads acquisition targets, not physical correspondences.
    selected = [min(candidates, key=lambda x: tuple(x[1]))]
    while len(selected) < min(6, len(candidates)):
        selected.append(max((p for p in candidates if p not in selected),
                            key=lambda p: min(math.dist(p[1], q[1]) for q in selected)))
    return [dict(id=f'observation-{index+1}', role='fit' if index < 3 else 'holdout', image=uv,
                 world=None, worldEvidence=None, feature=f'UNIDENTIFIED-vertex-{index+1}',
                 region='UNREVIEWED', imageLocator=locator) for index, (locator, uv) in enumerate(selected)]


def lab_clipping(raw, group, transform, native_size):
    """Measure opaque source pixels lost by the declared projection, not game truth."""
    root = inspect_svg(raw)
    width, height = 720, 586
    if root.get('viewBox') != '0 0 720 586':
        raise ValueError('Lab clipping viewBox changed')
    a, b, c, d, tx, ty = transform
    if abs(b)+abs(c) > 1e-9 or min(a, d) <= 0:
        raise ValueError('Lab clipping requires declared axis-aligned mapping')
    for node in list(root):
        if node.tag.endswith('}g') and node.get('id') != group:
            root.remove(node)
    for node in root.iter():
        if 'class' in node.attrib:
            node.set('class', ' '.join(v for v in node.get('class').split() if v != 'shadow'))
    image = raster_svg(ET.tostring(root, encoding='unicode'), (width*4, height*4))
    opaque = image.getchannel('A').point(lambda value: 255 if value >= 250 else 0)
    left, top = max(0, math.ceil(-tx/a*4-.5)), max(0, math.ceil(-ty/d*4-.5))
    right = min(width*4, math.floor((native_size[0]-tx)/a*4-.5)+1)
    bottom = min(height*4, math.floor((native_size[1]-ty)/d*4-.5)+1)
    retained = opaque.crop((left, top, right, bottom))
    return dict(renderSize=list(image.size), alphaThreshold=250, shadowFilterRemoved=True,
                retainedPixelRectangle=[left, top, right, bottom],
                opaqueSourcePixels=opaque.histogram()[255],
                clippedOpaquePixels=opaque.histogram()[255]-retained.histogram()[255],
                topClippedSourceV=[0, max(0, -ty/d)],
                evidence='Source-calibrated raster diagnostic only; independent physical geometry still UNKNOWN')


def prepare(assets, customs_upstream, lab_upstream, output):
    if output.exists():
        raise ValueError('new output directory required')
    for path in (output.absolute().parent, customs_upstream.absolute(), lab_upstream.absolute()):
        for ancestor in (path, *path.parents):
            if ancestor.exists():
                reject_reparse(ancestor)
    inputs = {}
    for name in PINS:
        path = customs_upstream/name
        reject_reparse(path)
        if path.stat().st_size > 1024*1024:
            raise ValueError('source bound')
        inputs[name] = verify_source(name, path.read_bytes())
    lab = load_inputs(LAB, lab_upstream)
    config = json.loads(inputs['Customs.jsonc'].decode('utf-8-sig').split('"DefaultLevel"')[0].rstrip().rstrip(',')+'}')
    lab_config = json.loads(lab['config.jsonc'].decode('utf-8-sig').split('"DefaultLevel"')[0].rstrip().rstrip(',')+'}')
    cases = [(MAP_ID, 'customs', config, [(floor, inputs['Customs-'+name+'.svg'], name,
                                          source_url('Customs-'+name+'.svg')) for floor, name in FLOORS.items()]),
             (LAB, 'lab', lab_config, [(floor, lab['SOURCE.svg'], name, sources(LAB)['SOURCE.svg'][0])
                                      for floor, name in CASES[0]['floors'].items()])]
    products, diagnostics = {}, []
    refs = {r['mapId']: r for r in rows(assets, 'map_references.tsv')}
    for map_id, slug, config, floor_inputs in cases:
        document = dict(schemaVersion=1, mapId=map_id, sources={}, floors=[])
        uri = source_url('Customs.jsonc') if map_id == MAP_ID else sources(LAB)['config.jsonc'][0]
        config_raw = inputs['Customs.jsonc'] if map_id == MAP_ID else lab['config.jsonc']
        document['sources']['calibration'] = dict(uri=uri, revision=uri.split('/')[5],
                                                 sha256=hashlib.sha256(config_raw).hexdigest(), lineage='SPT-'+slug+'-calibration-annotations')
        for floor, raw, group, uri in floor_inputs:
            root = inspect_svg(raw)
            view = [float(x) for x in root.get('viewBox').split()]
            source_id = 'image-'+floor
            document['sources'][source_id] = dict(uri=uri, revision=uri.split('/')[5], sha256=hashlib.sha256(raw).hexdigest(), lineage='Shebuka-'+slug+'-artwork')
            bounds = [config['Bounds']['Min'][k] for k in ('x', 'y')] + [config['Bounds']['Max'][k] for k in ('x', 'y')]
            points = select_observations(root, group, view)
            document['floors'].append(dict(floorId=floor, imageSource=source_id, calibrationSource='calibration', sourceBounds=bounds,
                                          rotation=config['CoordinateRotation'], viewBox=view, points=points))
            native = refs[map_id]
            source_projection = projection(bounds, config['CoordinateRotation'], view)
            native_projection = projection([float(native[k]) for k in ('minX', 'minZ', 'maxX', 'maxZ')],
                                           float(native['rotation']), [0, 0, float(native['width']), float(native['height'])])
            diagnostics.append(dict(mapId=map_id, floorId=floor, sourceWorldToImage=source_projection,
                                    sourceImageToWorld=inverse(source_projection),
                                    sourceImageToNative=compose(native_projection, inverse(source_projection)),
                                    evidence='Analytical source metadata only; NOT independent geometry validation'))
            if map_id == LAB:
                diagnostics[-1]['clipping'] = lab_clipping(raw, group, diagnostics[-1]['sourceImageToNative'],
                                                         (float(native['width']), float(native['height'])))
            for node in list(root):
                if node.tag.endswith('}g') and node.get('id') != group:
                    root.remove(node)
            overlay = ET.SubElement(root, '{http://www.w3.org/2000/svg}g')
            for point in points:
                u, v = point['image']
                ET.SubElement(overlay, '{http://www.w3.org/2000/svg}circle', cx=str(u), cy=str(v), r='2', fill='red')
                text = ET.SubElement(overlay, '{http://www.w3.org/2000/svg}text', x=str(u+3), y=str(v), fill='red', **{'font-size': '10'})
                text.text = point['id']+' UNKNOWN'
            products[slug+'/'+floor+'.observations.svg'] = ET.tostring(root, encoding='utf-8')
        report = calibrate(document)
        products[slug+'/controls.json'] = (json.dumps(document, sort_keys=True, indent=2)+'\n').encode()
        products[slug+'/report.json'] = (json.dumps(report, sort_keys=True, indent=2)+'\n').encode()
        products[slug+'/report.md'] = markdown(report).encode()
        products[slug+'/residuals.svg'] = residual_svg(report).encode()
        license_raw = inputs['LICENSE.md'] if slug == 'customs' else lab['LICENSE.txt']
        products[slug+'/LICENSE.txt'] = license_raw
        products[slug+'/UPSTREAM-README.md'] = inputs['README.md'] if slug == 'customs' else lab['README.md']
        products[slug+'/SOURCE.md'] = ('# Local acquisition targets, NOT verified calibration\n\nOriginal artwork: Shebuka; split-layer modifications: acidphantasm where applicable. '
            'Source revisions and SHA-256 are recorded in controls.json. Full CC BY-NC-SA 4.0 license retained. '
            'Noven changes: select a floor, mark directly observed SVG vertices, retain UNKNOWN world counterparts. '
            'All adaptations CC BY-NC-SA 4.0; actual use noncommercial. Official features free; cheating prohibited. No endorsement. '
            'A vertex is not yet a door/landmark; identify the same physical feature before accepting it. Original sources remain unchanged.\n').encode()
    products['projection-diagnostics.json'] = (json.dumps(diagnostics, sort_keys=True, indent=2)+'\n').encode()
    if sum(map(len, products.values())) > 2*1024*1024:
        raise ValueError('acquisition output budget')
    output.mkdir(parents=True, exist_ok=False)
    for name, raw in products.items():
        path = output/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return diagnostics


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('assets', 'customs-upstream', 'lab-upstream', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    prepare(args.assets, args.customs_upstream, args.lab_upstream, args.output)
