"""Entirely synthetic images/coordinates; no actual game measurement acceptance."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from import_screenshot_geometry import CONFIRMATIONS, import_measurements, main

MAP_ID = '56f40101d2720b2a4d8b45d6'


def template():
    return dict(schemaVersion=1, mapId=MAP_ID,
                sources=dict(image=dict(uri='synthetic:image', revision='test-only', sha256='a'*64, lineage='SYNTHETIC-art'),
                             calibration=dict(uri='synthetic:config', revision='test-only', sha256='b'*64, lineage='SYNTHETIC-config')),
                floors=[dict(floorId='4th_Floor', imageSource='image', calibrationSource='calibration',
                             viewBox=[0, 0, 100, 100], sourceBounds=[0, 0, 100, 100], rotation=0, points=[])])


def sample(root):
    rows = []
    for index, uv in enumerate(([10, 10], [80, 20], [20, 80], [80, 80], [40, 30], [30, 60])):
        filename = f'2026-10-28[12-00]_{uv[0]:.2f}, 20.00, {100-uv[1]:.2f}_0, 0, 0, 1_12 (0).png'
        path = root/filename
        Image.new('RGB', (8, 8), (index*25, 20, 40)).save(path, format='PNG')
        rows.append(dict(id=f'SYNTHETIC-{index}', floorId='4th_Floor', originalFilename=filename,
                         screenshotSha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         role='fit' if index < 3 else 'holdout', region=f'SYNTHETIC-building-{index%2}',
                         landmarkName=f'SYNTHETIC-player-station-{index}', image=list(uv), imageSha256='a'*64,
                         imageLocator=f'SYNTHETIC-vertex-{index}', imageSelectionMethod='manual-source-svg',
                         worldSemantic='player-position', imageSemantic='player-position', uncertaintyWorld=.2,
                         uncertaintyEvidence='SYNTHETIC TEST ONLY', coordinateReferenceEvidence='SYNTHETIC TEST ONLY',
                         gameVersion='SYNTHETIC TEST ONLY', mode='PvE', sessionId='SYNTHETIC', evidenceSource='SYNTHETIC',
                         reviewer='SYNTHETIC', reviewRecord='SYNTHETIC TEST ONLY',
                         confirmations={flag: True for flag in CONFIRMATIONS}))
    return dict(schemaVersion=1, mapId=MAP_ID, measurements=rows)


class ScreenshotGeometryTests(unittest.TestCase):
    def test_synthetic_bridge_preserves_xyz_and_split_not_native_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); annotations = sample(root); base = template()
            saved, old_base = copy.deepcopy(annotations), copy.deepcopy(base)
            controls, records, report = import_measurements(base, annotations, root, 'a'*64)
            self.assertEqual(annotations, saved); self.assertEqual(base, old_base)
            self.assertEqual(report['floors'][0]['acceptedFit'], 3)
            self.assertEqual(report['floors'][0]['acceptedHoldout'], 3)
            self.assertLess(report['floors'][0]['models']['identity']['heldOut']['maximum'], 1e-9)
            self.assertFalse(report['publicationAuthorized'])
            self.assertIn('PENDING', report['measurementImport']['nativeCaptureAcceptance'])
            self.assertEqual(records['measurements'][0]['capture']['worldXYZ'], [10, 20, 90])
            point = controls['floors'][0]['points'][0]
            self.assertEqual(point['world'], [10, 90])
            self.assertEqual(point['worldEvidence']['worldXYZ'], [10, 20, 90])
            self.assertEqual(point['worldEvidence']['originalFilename'], annotations['measurements'][0]['originalFilename'])
            self.assertEqual(import_measurements(base, annotations, root, 'a'*64), (controls, records, report))

    def test_unconfirmed_stays_pending_without_fabricated_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); annotations = sample(root)
            for row in annotations['measurements']:
                row['confirmations']['coordinateReference'] = False
            controls, records, report = import_measurements(template(), annotations, root, 'a'*64)
            self.assertEqual(controls['floors'][0]['points'], [])
            self.assertEqual(report['floors'][0]['heldOut']['rmse'], 'UNKNOWN')
            self.assertTrue(all(r['status'] == 'PENDING' for r in records['measurements']))

    def test_player_position_never_becomes_boundary_or_object(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); annotations = sample(root)
            for semantic in ('room-boundary', 'building-corner', 'extraction-area-center', 'interactive-object'):
                for row in annotations['measurements']:
                    row['worldSemantic'] = semantic; row['imageSemantic'] = semantic
                controls, _, report = import_measurements(template(), annotations, root, 'a'*64)
                self.assertEqual(controls['floors'][0]['points'], [])
                self.assertEqual(report['floors'][0]['status'], 'UNKNOWN')

    def test_manual_pick_is_required_not_world_projection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); annotations = sample(root)
            for row in annotations['measurements']:
                row['imageSelectionMethod'] = 'world-projected'
            self.assertEqual(import_measurements(template(), annotations, root, 'a'*64)[0]['floors'][0]['points'], [])

    def test_missing_or_excessive_uncertainty_never_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); annotations = sample(root)
            for value in (None, 0, .251):
                for row in annotations['measurements']:
                    row['uncertaintyWorld'] = value
                report = import_measurements(template(), annotations, root, 'a'*64)[2]
                self.assertEqual(report['floors'][0]['status'], 'UNKNOWN')
            annotations['measurements'][0]['uncertaintyWorld'] = float('nan')
            with self.assertRaises(ValueError):
                import_measurements(template(), annotations, root, 'a'*64)

    def test_changed_screenshot_hash_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); annotations = sample(root)
            path = root/annotations['measurements'][0]['originalFilename']
            Image.new('RGB', (8, 8), 'blue').save(path)
            with self.assertRaisesRegex(ValueError, 'changed'):
                import_measurements(template(), annotations, root, 'a'*64)

    def test_duplicate_screenshot_is_not_independent_holdout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); annotations = sample(root)
            repeated = copy.deepcopy(annotations['measurements'][0]); repeated['id'] = 'duplicate'; repeated['role'] = 'holdout'
            annotations['measurements'].append(repeated)
            with self.assertRaisesRegex(ValueError, 'duplicate independent'):
                import_measurements(template(), annotations, root, 'a'*64)

    def test_map_floor_image_and_traversal_fail_closed(self):
        mutations = [lambda d: d.update(mapId='5b0fc42d86f7744a585f9105'),
                     lambda d: d['measurements'][0].update(floorId='other'),
                     lambda d: d['measurements'][0].update(imageSha256='c'*64),
                     lambda d: d['measurements'][0].update(originalFilename='../image.png'),
                     lambda d: d['measurements'][0].update(image=[1000, 4])]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); original = sample(root)
            for mutate in mutations:
                annotations = copy.deepcopy(original); mutate(annotations)
                with self.assertRaises(ValueError):
                    import_measurements(template(), annotations, root, 'a'*64)
            with self.assertRaises(ValueError):
                import_measurements(template(), original, root, 'c'*64)

    def test_empty_inventory_can_report_unknown_without_creating_capture_root(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory)/'no-captures'
            report = import_measurements(template(), dict(schemaVersion=1, mapId=None, measurements=[]), missing, 'a'*64)[2]
            self.assertEqual(report['measurementImport']['records'], 0)
            self.assertEqual(report['floors'][0]['status'], 'UNKNOWN')
            self.assertFalse(missing.exists())

    def test_cli_writes_only_new_evidence_and_keeps_screenshots(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); captures = root/'captures'; captures.mkdir()
            annotations = sample(captures); base = template()
            image = root/'SYNTHETIC.svg'
            image.write_bytes(b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M 0 0 L 50 50"/></svg>')
            image_hash = hashlib.sha256(image.read_bytes()).hexdigest()
            base['sources']['image']['sha256'] = image_hash
            for row in annotations['measurements']:
                row['imageSha256'] = image_hash
            (root/'template.json').write_text(json.dumps(base), encoding='utf-8')
            (root/'annotations.json').write_text(json.dumps(annotations), encoding='utf-8')
            before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in captures.iterdir()}
            argv = ['tool', '--directory', str(captures), '--template', str(root/'template.json'),
                    '--annotations', str(root/'annotations.json'), '--image', str(image), '--output', str(root/'output')]
            with patch.object(sys, 'argv', argv):
                main()
            self.assertEqual(len(list((root/'output').iterdir())), 5)
            self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in captures.iterdir()})
            report = json.loads((root/'output/report.json').read_bytes())
            self.assertFalse(report['publicationAuthorized'])
            self.assertIn('PENDING_INDEPENDENT_USER_GAME_SAMPLE_REVIEW', (root/'output/report.md').read_text(encoding='utf-8'))
            with patch.object(sys, 'argv', argv), self.assertRaises(FileExistsError):
                main()

    def test_handwritten_world_override_is_not_used(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); annotations = sample(root)
            annotations['measurements'][0]['worldXYZ'] = [999, 999, 999]
            controls, records, _ = import_measurements(template(), annotations, root, 'a'*64)
            self.assertEqual(controls['floors'][0]['points'][0]['world'], [10, 90])
            self.assertEqual(records['measurements'][0]['capture']['worldXYZ'], [10, 20, 90])

    def test_each_confirmation_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); original = sample(root)
            for flag in CONFIRMATIONS:
                annotations = copy.deepcopy(original)
                for row in annotations['measurements']:
                    row['confirmations'][flag] = False
                self.assertEqual(import_measurements(template(), annotations, root, 'a'*64)[0]['floors'][0]['points'], [])


if __name__ == '__main__':
    unittest.main()
