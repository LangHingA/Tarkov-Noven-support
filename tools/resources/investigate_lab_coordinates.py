"""Offline Lab coordinate diagnostics; never changes assets or publishes resources.

Legacy JSONC world annotations are NOT independently measured SVG pixel landmarks.
The cross-validation below diagnoses the world frame, not map geometry accuracy.
"""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

MODELS = ('identity', 'translation', 'rigid', 'uniform', 'similarity', 'nonuniform', 'affine')
LAB = '5b0fc42d86f7744a585f9105'
LOCKS = (
    ('TerraGroup Manager\'s Office', 0, 'ead614596fd574cca7efcb7ab67adce6b93f7f29'),
    ('TerraGroup Manager\'s Office', 1, '9b5b989dece7e75befe2cb87c1973f04b7553fae'),
    ('Weapon Testing Area', 0, '96da8622c621cb42229d48719286ce1d746033f9'),
    ('Weapon Testing Area', 1, 'ec956305ecff4a40051d641ec96eecfcf30c930e'),
    ('Infirmary (Blue)', 0, '2e653b6dd3ae2033cd93efc74c338f2a30ce9ebb'),
    ('Sterile Lab (Green)', 0, '05963f7358b42b260526df45e60b5755d09c0366'),
    ('Card with a Blue Marking', 0, 'da8237013a32b58c270653afb9a43f3175816920'),
    ('Security #2 (Yellow)', 0, 'ecb5504f3bfbb161c114e263611c30bf89b8a0c2'),
    ('Test Room (Black)', 0, '6b9c65d4d24e1df1f5df7cf787875741de5aa980'),
    ('Test Room (Black)', 1, '577b9b90d0f1d11d15817ab2114deefb6307f964'),
    ('Security Office (Violet)', 0, '8b40ef064ab348da611f5f26e4bdf2d90a963cea'),
    ('Security Office (Red)', 0, '035905a190db56d233238cdd56c01cd8f79ed0c0'),
    ('Arsenal Storage', 0, '2154804303b2611819f44d335a087e3e16d935ed'),
    ('Residential Unit', 0, 'c52d804746ec12f539fb4a82896bb38e1d2e2659'),
)
SWITCHES = (
    ('Medical Block Elevator Power', 'switch_00409_power'),
    ('Main Elevator Power Button', 'switch_00404_Power'),
    ('Open Parking Gate', 'switch_autoId_00014_EXFIL_Console_trigger'),
    ('Water Level Switch', 'switch_00415_Pump_button'),
    ('Disable Parking Gate Alarm', 'switch_00418_Disable_alarm_trigger'),
)
TRAIN = {"TerraGroup Manager's Office#0", 'Weapon Testing Area#0',
         'Infirmary (Blue)#0', 'Security #2 (Yellow)#0',
         'Medical Block Elevator Power', 'Main Elevator Power Button'}
EXTRACTS = {
    'Cargo Elevator': 'lab_Elevator_Cargo', 'Main Elevator': 'lab_Elevator_Main',
    'Medical Block Elevator': 'lab_Elevator_Med', 'Sewage Conduit': 'lab_Under_Storage_Collector',
    'Ventilation Shaft': 'lab_Vent', 'Parking Gate': 'lab_Parking_Gate', 'Hangar Gate': 'lab_Hangar_Gate',
}


def apply(transform, point):
    a, b, c, d, tx, ty = transform
    x, y = point
    return a*x+b*y+tx, c*x+d*y+ty


def fit(pairs, model):
    if model not in MODELS or len(pairs) < 3:
        raise ValueError('unknown model or insufficient observations')
    if model == 'identity':
        return (1, 0, 0, 1, 0, 0)
    n = len(pairs)
    sx, sy = (sum(p[0][i] for p in pairs)/n for i in (0, 1))
    dx, dy = (sum(p[1][i] for p in pairs)/n for i in (0, 1))
    centered = [((s[0]-sx, s[1]-sy), (t[0]-dx, t[1]-dy)) for s, t in pairs]
    xx = sum(s[0]**2 for s, t in centered)
    yy = sum(s[1]**2 for s, t in centered)
    xy = sum(s[0]*s[1] for s, t in centered)
    if min(xx, yy) < 1e-12:
        raise ValueError('degenerate controls')
    dot = sum(s[0]*t[0]+s[1]*t[1] for s, t in centered)
    cross = sum(s[0]*t[1]-s[1]*t[0] for s, t in centered)
    a, b, c, d = 1., 0., 0., 1.
    if model in ('rigid', 'similarity'):
        norm = math.hypot(dot, cross)
        if norm < 1e-12:
            raise ValueError('undefined rotation')
        scale = norm/(xx+yy) if model == 'similarity' else 1.
        a, b, c, d = scale*dot/norm, -scale*cross/norm, scale*cross/norm, scale*dot/norm
    elif model == 'uniform':
        a = d = dot/(xx+yy)
    elif model == 'nonuniform':
        a = sum(s[0]*t[0] for s, t in centered)/xx
        d = sum(s[1]*t[1] for s, t in centered)/yy
    elif model == 'affine':
        determinant = xx*yy-xy*xy
        if abs(determinant) < 1e-12*xx*yy:
            raise ValueError('collinear affine controls')
        def solve(axis):
            u = sum(s[0]*t[axis] for s, t in centered)
            v = sum(s[1]*t[axis] for s, t in centered)
            return (u*yy-v*xy)/determinant, (v*xx-u*xy)/determinant
        a, b = solve(0)
        c, d = solve(1)
    return a, b, c, d, dx-a*sx-b*sy, dy-c*sx-d*sy


def errors(transform, pairs):
    residuals = [math.dist(apply(transform, s), t) for s, t in pairs]
    return dict(rmse=math.sqrt(sum(e*e for e in residuals)/len(residuals)), maximum=max(residuals))


def bounds_center(extract):
    outline = extract['outline']
    return tuple((min(p[a] for p in outline)+max(p[a] for p in outline))/2 for a in ('x', 'z'))


def investigate(config, api):
    # 输入只读；JSONC 仅去掉整行注释，不损坏 https:// 来源字符串。
    # Read-only inputs; remove comment-only JSONC lines without damaging URLs.
    legacy = json.loads(re.sub(r'(?m)^\s*//[^\n]*', '', config.read_text(encoding='utf-8')))
    current = json.loads(api.read_bytes())['data']['maps'][LAB]
    observations = []
    def add(label, source, destination):
        height = source['z']
        observations.append(dict(label=label, floor='Technical' if height < -.9 else 'Second_Level' if height >= 3 else 'Base',
                                 source=[source['x'], source['y']], target=[destination['x'], destination['z']],
                                 train=label in TRAIN))
    for name, occurrence, identity in LOCKS:
        source = [p for p in legacy['StaticMarkers'] if p['Text'] == name][occurrence]
        target = next(p for p in current['locks'] if p['id'] == identity)
        if target['key'] != source['AssociatedItemId']:
            raise ValueError('landmark key identity changed')
        add(f'{name}#{occurrence}', source['Position'], target['position'])
    for name, identity in SWITCHES:
        source = next(p for p in legacy['StaticMarkers'] if p['Text'] == name)
        target = next(p for p in current['switches'] if p['name'] == identity)
        add(name, source['Position'], target['position'])
    train = [(o['source'], o['target']) for o in observations if o['train']]
    held = [(o['source'], o['target']) for o in observations if not o['train']]
    result = dict(interpretation='world annotations only; NOT independent SVG-pixel or live-game calibration',
                  hashes={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (config, api)},
                  observations=observations, models={}, extracts=[])
    for model in MODELS:
        transform = fit(train, model)
        predictions = []
        for i, observation in enumerate(observations):
            others = [(p['source'], p['target']) for k, p in enumerate(observations) if k != i]
            prediction = apply(fit(others, model), observation['source'])
            predictions.append((prediction, observation['target']))
        result['models'][model] = dict(transform=transform, training=errors(transform, train), heldOut=errors(transform, held),
                                      leaveOneOut=errors((1, 0, 0, 1, 0, 0), predictions))
    for name, identity in EXTRACTS.items():
        old = next(p['Position'] for p in legacy['StaticMarkers'] if p['Text'] == name)
        new = next(p for p in current['extracts'] if p['name'] == identity)
        outline = new['outline']
        middle = bounds_center(new)
        entry = dict(name=name, oldPoint=[old['x'], old['y']], newPoint=[new['position']['x'], new['position']['z']],
                     oldHeight=old['z'], newHeight=new['position']['y'], boundsCenter=middle,
                     centerResidual=math.dist(middle, [new['position']['x'], new['position']['z']]),
                     pointDifference=math.dist([old['x'], old['y']], [new['position']['x'], new['position']['z']]),
                     zBounds=[min(p['z'] for p in outline), max(p['z'] for p in outline)])
        result['extracts'].append(entry)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-config', required=True, type=Path)
    parser.add_argument('--api-snapshot', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(investigate(args.legacy_config, args.api_snapshot), ensure_ascii=True, indent=2))
