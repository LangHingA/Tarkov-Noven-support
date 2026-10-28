import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

from prepare_recovery_svg import LAB, RESERVE, load_inputs, prepare, rows, sources


class RecoverySvgTests(unittest.TestCase):
    assets = Path(__file__).resolve().parents[2] / 'assets'

    def inputs(self, map_id):
        data = {name: b'Original synthetic test notice' for name in sources(map_id)}
        data['config.jsonc'] = json.dumps(dict(Bounds=dict(Min=dict(x=0, y=0), Max=dict(x=10, y=10)),
                                              CoordinateRotation=180, StaticMarkers=[])).encode()
        groups = ['Ground_Level', 'Bunkers'] if map_id == RESERVE else ['Technical_Level', 'First_Level', 'Second_Level']
        for name in data:
            if name.endswith('.svg'):
                selected = [groups[0]] if name == 'Ground.svg' else [groups[1]] if name == 'Bunkers.svg' else groups
                data[name] = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">' +
                              ''.join(f'<g id="{g}"><rect width="5" height="5"/></g>' for g in selected) + '</svg>').encode()
        return data

    def generate(self, map_id, path):
        with patch('prepare_recovery_svg.load_inputs', return_value=self.inputs(map_id)), \
             patch('prepare_recovery_svg.convert', return_value=Image.new('RGBA', (16, 12), 'red')):
            return prepare(self.assets, map_id, path)

    def test_reserve_missing_floors_never_become_complete_package(self):
        with tempfile.TemporaryDirectory(prefix='noven-recovery-') as root:
            output = Path(root) / 'partial'
            result = self.generate(RESERVE, output)
            self.assertEqual(set(result['floors']), {'Ground_Level', 'Bunkers'})
            self.assertEqual(result['missingFloors'], ['2nd_Floor', '3rd_Floor', '4th_Floor', '5th_Floor'])
            self.assertFalse((output / 'package').exists())
            self.assertFalse(result['publishable'])
            self.assertIsNone(result['heldOutRmse'])

    def test_lab_candidate_is_deterministic_not_geometry_acceptance(self):
        with tempfile.TemporaryDirectory(prefix='noven-recovery-') as root:
            root = Path(root)
            a, b = (self.generate(LAB, root / name) for name in ('first', 'repeat'))
            self.assertEqual(a, b)
            self.assertEqual(len(a['floors']), 3)
            self.assertEqual(a['missingFloors'], [])
            self.assertEqual(a['status'], 'BLOCKED')
            self.assertFalse(a['independentGeometryVerified'])
            self.assertFalse(a['publishable'])
            packages = [root / name / 'package' / a['package']['artifact'] for name in ('first', 'repeat')]
            self.assertEqual(packages[0].read_bytes(), packages[1].read_bytes())
            self.assertEqual(hashlib.sha256(packages[0].read_bytes()).hexdigest(), a['package']['sha256'])
            self.assertTrue((root / 'first/input/maps/the-lab/sources/Base/UPSTREAM-README.md').is_file())
            self.assertFalse(any(p.suffix == '.jsonc' for p in (root / 'first/input').rglob('*')))

    def test_never_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory(prefix='noven-recovery-') as root:
            output = Path(root)
            (output / 'keep.txt').write_text('keep')
            with patch('prepare_recovery_svg.load_inputs') as network, self.assertRaisesRegex(ValueError, 'NEW'):
                prepare(self.assets, LAB, output)
            network.assert_not_called()
            self.assertEqual((output / 'keep.txt').read_text(), 'keep')

    def test_size_budget_fails_before_output_creation(self):
        with tempfile.TemporaryDirectory(prefix='noven-recovery-') as root:
            output = Path(root) / 'never-created'
            with patch('prepare_recovery_svg.MAX_OUTPUT', 1), self.assertRaisesRegex(ValueError, 'before writing'):
                self.generate(LAB, output)
            self.assertFalse(output.exists())

    def test_changed_pve_contract_rejects_before_fetch(self):
        def altered(assets, name):
            result = rows(assets, name)
            return [r for r in result if not (r.get('mapId') == LAB and r.get('floorId') == 'Technical')] if name == 'pve/map_floors.tsv' else result
        with tempfile.TemporaryDirectory(prefix='noven-recovery-') as root:
            with patch('prepare_recovery_svg.rows', side_effect=altered), \
                 patch('prepare_recovery_svg.load_inputs') as fetch, self.assertRaisesRegex(ValueError, 'contract differs'):
                prepare(self.assets, LAB, Path(root) / 'new')
            fetch.assert_not_called()

    def test_wrong_source_hash_rejected_without_network(self):
        with tempfile.TemporaryDirectory(prefix='noven-recovery-') as root:
            root = Path(root)
            (root / 'Ground.svg').write_bytes(b'not the pinned SVG')
            with patch('urllib.request.urlopen') as fetch, self.assertRaisesRegex(ValueError, 'hash mismatch'):
                load_inputs(RESERVE, root)
            fetch.assert_not_called()
        with self.assertRaisesRegex(ValueError, 'unsupported'):
            sources('arbitrary-map')


if __name__ == '__main__':
    unittest.main()
