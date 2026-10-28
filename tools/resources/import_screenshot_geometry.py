"""Manual native-screenshot/image pairs -> existing Phase 2 calibration, offline.

No world->image picking, coordinate offsets, map generation or publication.
Manual declarations never prove a screenshot was actually created by the game.
"""
import argparse
import copy
import hashlib
import json
import math
import re
from pathlib import Path

from calibrate_map_geometry import calibrate, markdown, numbers, read_document, residual_svg, validate
from eft_screenshot_capture import MAX_FILES, MAX_TOTAL_BYTES, check_path, new_output, read_capture
from prepare_additional_svg import inspect_svg

CONFIRMATIONS = ('nativeOrigin', 'mapAndFloor', 'coordinateReference', 'samePhysicalEntity',
                 'independentImagePick', 'independentWorldSource')
REQUIRED_TEXT = ('region', 'landmarkName', 'imageLocator', 'gameVersion', 'sessionId', 'evidenceSource',
                 'coordinateReferenceEvidence', 'uncertaintyEvidence', 'reviewer', 'reviewRecord')


def text_present(value):
    return isinstance(value, str) and 0 < len(value.strip()) <= 512 and not any(ord(c) < 32 for c in value)


def pending_reasons(row):
    issues = []
    for field in REQUIRED_TEXT:
        if not text_present(row.get(field)):
            issues.append('missing '+field)
    confirmations = row.get('confirmations', {})
    for flag in CONFIRMATIONS:
        if not isinstance(confirmations, dict) or confirmations.get(flag) is not True:
            issues.append('unconfirmed '+flag)
    if row.get('worldSemantic') != 'player-position' or row.get('imageSemantic') != 'player-position':
        issues.append('filename position cannot be substituted for a wall/corner/extract/object')
    if row.get('imageSelectionMethod') != 'manual-source-svg':
        issues.append('image must be independently picked in the original source SVG viewBox')
    if row.get('image') is None or row.get('imageSha256') is None:
        issues.append('missing independently observed image position/identity')
    if row.get('role') not in ('fit', 'holdout') or row.get('mode') not in ('PvP', 'PvE'):
        issues.append('missing fit/holdout role or PvP/PvE mode')
    uncertainty = row.get('uncertaintyWorld')
    if type(uncertainty) not in (int, float) or not math.isfinite(uncertainty) or not 0 < uncertainty <= .25:
        issues.append('combined picking/reference uncertainty must be substantiated and within (0,0.25]')
    return issues


def import_measurements(template, annotations, directory, image_sha256):
    json.dumps(annotations, allow_nan=False)
    validate(template)
    if type(annotations.get('schemaVersion')) is not int or annotations['schemaVersion'] != 1:
        raise ValueError('unsupported measurement schema')
    records = annotations['measurements']
    if not isinstance(records, list) or len(records) > MAX_FILES:
        raise ValueError('measurement count bound')
    if annotations.get('mapId') != template['mapId'] and not (not records and annotations.get('mapId') is None):
        raise ValueError('measurement/template stable map identity differs')
    sources = template['sources']
    if image_sha256 not in {sources[f['imageSource']]['sha256'] for f in template['floors']}:
        raise ValueError('local source SVG hash differs from pinned template')
    controls = copy.deepcopy(template)
    floors = {f['floorId']: f for f in controls['floors']}
    for floor in floors.values():
        floor['points'] = []
    measurements, seen_ids, seen_images, total = [], set(), set(), 0
    for row in records:
        identity = row.get('id')
        if not isinstance(identity, str) or not re.fullmatch('[A-Za-z0-9_-]{1,64}', identity) or identity in seen_ids:
            raise ValueError('invalid/duplicate measurement identity')
        seen_ids.add(identity)
        if row.get('floorId') not in floors:
            raise ValueError('unknown floor; do not infer it from a filename')
        floor = floors[row['floorId']]
        expected_image = sources[floor['imageSource']]['sha256']
        if expected_image != image_sha256 or row.get('imageSha256') not in (None, expected_image):
            raise ValueError('wrong image/floor identity; process each source SVG separately')
        expected = row.get('screenshotSha256')
        if not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected):
            raise ValueError('missing expected screenshot hash')
        capture = read_capture(directory, row['originalFilename'])
        if capture['screenshotSha256'] != expected:
            raise ValueError('screenshot bytes changed since capture inventory')
        if expected in seen_images:
            raise ValueError('one screenshot cannot supply duplicate independent observations')
        seen_images.add(expected)
        total += capture['fileBytes']
        if total > MAX_TOTAL_BYTES:
            raise ValueError('measurement collection size bound')
        image = row.get('image')
        if image is not None:
            numbers(image, 2)
            vx, vy, width, height = floor['viewBox']
            if not (vx <= image[0] <= vx+width and vy <= image[1] <= vy+height):
                raise ValueError('manual image position outside source viewBox')
        issues = pending_reasons(row)
        measurements.append(dict(mapId=template['mapId'], floorId=row['floorId'], annotation=copy.deepcopy(row),
                                 capture=capture, status='PENDING' if issues else 'DECLARED_MATCH_READY_FOR_NUMERIC_REVIEW', issues=issues))
        if issues:
            continue
        source_id = 'capture-'+expected
        controls['sources'][source_id] = dict(uri='local-eft-native-screenshot:'+capture['originalFilename'],
                                             revision='sha256:'+expected, sha256=expected,
                                             lineage='native-screenshot-session:'+row['sessionId'])
        # 原始 XYZ 原样保留，校准只取 x/z；不把站位改成墙角，也不由世界投影生成 UV。
        # Preserve raw XYZ; calibration uses x/z without boundary offsets or world-derived UV.
        floor['points'].append(dict(id=identity, role=row['role'], feature=row['landmarkName'], region=row['region'],
                                   image=image.copy(), imageLocator=row['imageLocator'],
                                   world=[capture['worldXYZ'][0], capture['worldXYZ'][2]],
                                   worldEvidence=dict(source=source_id, method='visible-manual-survey',
                                                      locator=capture['originalFilename'], gameVersion=row['gameVersion'],
                                                      samePhysicalFeatureReviewed=True, reviewRecord=row['reviewRecord'],
                                                      pickingUncertaintyWorld=row['uncertaintyWorld'],
                                                      worldXYZ=capture['worldXYZ'], mode=row['mode'],
                                                      coordinateReferenceEvidence=row['coordinateReferenceEvidence'],
                                                      uncertaintyEvidence=row['uncertaintyEvidence'], reviewer=row['reviewer'],
                                                      evidenceSource=row['evidenceSource'],
                                                      screenshotSha256=expected, originalFilename=capture['originalFilename'],
                                                      worldSemantic=row['worldSemantic'], imageSemantic=row['imageSemantic'])))
    report = calibrate(controls)
    report['measurementImport'] = dict(records=len(records), declaredMatches=sum(not m['issues'] for m in measurements),
                                     pending=sum(bool(m['issues']) for m in measurements),
                                     nativeCaptureAcceptance='PENDING_INDEPENDENT_USER_GAME_SAMPLE_REVIEW',
                                     boundary='Hash and confirmation fields do not authenticate game origin, coordinates, physical identity or game build. No publication approval.')
    return controls, dict(schemaVersion=1, mapId=template['mapId'], measurements=measurements), report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True, help='Read-only native screenshot/explicit collection directory')
    parser.add_argument('--template', type=Path, required=True, help='Preserved Phase 2 controls.json')
    parser.add_argument('--annotations', type=Path, required=True, help='Manually completed measurement records')
    parser.add_argument('--image', type=Path, required=True, help='Exact pinned original SVG, not a renamed PNG or overlay')
    parser.add_argument('--output', type=Path, required=True, help='New directory outside screenshot collection')
    args = parser.parse_args()
    for path in (args.directory, args.template, args.annotations, args.image):
        check_path(path)
    if args.image.stat().st_size > 1024*1024:
        raise ValueError('source SVG size bound')
    with args.image.open('rb') as stream:
        source_svg = stream.read(1024*1024+1)
    if len(source_svg) > 1024*1024:
        raise ValueError('source SVG size bound')
    inspect_svg(source_svg)
    digest = hashlib.sha256(source_svg).hexdigest()
    controls, measurements, report = import_measurements(read_document(args.template), read_document(args.annotations), args.directory, digest)
    report['templateSha256'] = hashlib.sha256(args.template.read_bytes()).hexdigest()
    report['annotationsSha256'] = hashlib.sha256(args.annotations.read_bytes()).hexdigest()
    report['sourceSvgSha256'] = digest
    new_output(args.output, args.directory)
    for name, document in (('controls.json', controls), ('measurements.json', measurements), ('report.json', report)):
        (args.output/name).write_text(json.dumps(document, sort_keys=True, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    summary = report['measurementImport']
    note = ('\n## Native screenshot evidence\n\n'
            f'Records: {summary["records"]}; declared matches: {summary["declaredMatches"]}; pending: {summary["pending"]}.\n\n'
            f'Native capture acceptance: {summary["nativeCaptureAcceptance"]}.\n\n{summary["boundary"]}\n')
    (args.output/'report.md').write_text(markdown(report)+note, encoding='utf-8')
    (args.output/'residuals.svg').write_text(residual_svg(report), encoding='utf-8')
    print(json.dumps(report['measurementImport']))


if __name__ == '__main__':
    main()
