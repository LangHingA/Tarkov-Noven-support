import unittest
import xml.etree.ElementTree as ET

from prepare_geometry_requests import lab_clipping, select_observations, vertices


class ObservationTests(unittest.TestCase):
    def test_distinct_deterministic_vertices_never_invent_world_coordinates(self):
        root = ET.fromstring('<svg><g id="floor"><polygon points="0,0 90,0 90,90 0,90 20,30 70,60 40,70"/></g></svg>')
        points = select_observations(root, 'floor', [0, 0, 100, 100])
        self.assertEqual(points, select_observations(root, 'floor', [0, 0, 100, 100]))
        self.assertEqual(len(points), 6)
        self.assertEqual([p['role'] for p in points], ['fit']*3+['holdout']*3)
        self.assertTrue(all(p['world'] is None and p['region'] == 'UNREVIEWED' for p in points))
        self.assertEqual(len({tuple(p['image']) for p in points}), 6)

    def test_transform_ancestry_is_not_ignored(self):
        root = ET.fromstring('<svg><g transform="translate(4 5)"><polygon points="0,0 1,0 0,1"/></g><path d="M 3 -2 L 4 4"/></svg>')
        self.assertEqual([p for _, p in vertices(root)], [[3., -2.]])

    def test_empty_or_outside_is_not_a_placeholder(self):
        for body in ('', '<path d="M 300 400 L 500 600"/>'):
            root = ET.fromstring('<svg><g id="floor">'+body+'</g></svg>')
            with self.assertRaises(ValueError):
                select_observations(root, 'floor', [0, 0, 100, 100])

    def test_clipping_is_source_diagnostic_not_game_accuracy(self):
        raw = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 586"><g id="Technical_Level"><path d="M 10 0 H 30 V 30 H 10 Z" fill="blue"/></g></svg>'
        report = lab_clipping(raw, 'Technical_Level', (1, 0, 0, 1, 0, -10), (720, 586))
        self.assertEqual(report['clippedOpaquePixels'], 20*10*16)
        self.assertEqual(report['topClippedSourceV'], [0, 10])
        self.assertIn('UNKNOWN', report['evidence'])


if __name__ == '__main__':
    unittest.main()
