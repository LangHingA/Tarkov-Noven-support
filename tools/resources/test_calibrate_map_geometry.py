"""Synthetic numerical tests, not real map survey evidence."""
import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

from calibrate_map_geometry import apply, calibrate, compose, inverse, markdown, projection, read_document, residual_svg
from prepare_additional_svg import project


def sample():
    points = []
    # 刻意独立的拟合/留出集合；所有坐标和来源都是标记清楚的测试数据。
    # Explicitly synthetic, independent fit/holdout sets for testing only.
    for i, uv in enumerate(([10, 10], [80, 20], [20, 80], [80, 80], [40, 30], [30, 60])):
        points.append(dict(id=f'p{i}', role='fit' if i < 3 else 'holdout', image=uv, world=[uv[0], 100-uv[1]],
                           feature=f'corner-{i}', region=f'room-{i%2}', imageLocator=f'polygon vertex {i}',
                           worldEvidence=dict(source='survey', method='visible-manual-survey', locator=f'photo-{i}',
                                              samePhysicalFeatureReviewed=True, gameVersion='SYNTHETIC',
                                              reviewRecord='SYNTHETIC TEST ONLY', pickingUncertaintyWorld=.1)))
    return dict(schemaVersion=1, mapId='56f40101d2720b2a4d8b45d6',
                sources=dict(image=dict(uri='test:image', revision='synthetic', sha256='a'*64, lineage='synthetic-art'),
                             survey=dict(uri='test:survey', revision='synthetic', sha256='b'*64, lineage='synthetic-survey')),
                floors=[dict(floorId='Ground_Level', imageSource='image', sourceBounds=[0, 0, 100, 100],
                             rotation=0, viewBox=[0, 0, 100, 100], points=points)])


class CalibrationTests(unittest.TestCase):
    def test_projection_matches_generator_all_rotations_and_view_origin(self):
        bounds = [-372, -306, 698, 235]
        view = [11, -7, 1062.4827, 535.174]
        for rotation in (0, 37, 90, 180, 195.209, 270):
            transform = projection(bounds, rotation, view)
            for x, z in ((-372, -306), (698, 235), (85, -25)):
                expected = project(x, z, [bounds[:2], bounds[2:]], rotation, *view[2:])
                actual = apply(transform, (x, z))
                self.assertAlmostEqual(actual[0], expected[0]+view[0])
                self.assertAlmostEqual(actual[1], expected[1]+view[1])
                self.assertLess(math.dist(apply(inverse(transform), actual), (x, z)), 1e-9)

    def test_models_use_same_frozen_split_and_do_not_mutate_input(self):
        document = sample(); original = copy.deepcopy(document)
        result = calibrate(document)
        floor = result['floors'][0]
        self.assertEqual(document, original)
        self.assertEqual(floor['acceptedFit'], 3)
        self.assertEqual(floor['acceptedHoldout'], 3)
        self.assertEqual(len(floor['models']), 7)
        for model in floor['models'].values():
            self.assertLess(model['heldOut']['maximum'], 1e-9)
            self.assertTrue(model['numericPass'])
        self.assertFalse(result['publicationAuthorized'])
        self.assertNotIn('READY_FOR_PUBLICATION_REVIEW', json.dumps(result))
        self.assertIn('Ground_Level', markdown(result))
        self.assertIn('<svg', residual_svg(result))

    def test_held_out_error_not_removed_by_perfect_training(self):
        document = sample()
        document['floors'][0]['points'][-1]['world'][0] += 5
        for model in calibrate(document)['floors'][0]['models'].values():
            self.assertFalse(model['numericPass'])
            self.assertGreater(model['heldOut']['maximum'], 4.99)

    def test_missing_world_is_unknown_not_zero_or_fitted(self):
        document = sample()
        for point in document['floors'][0]['points']:
            point['world'] = None
        floor = calibrate(document)['floors'][0]
        self.assertEqual(floor['status'], 'UNKNOWN')
        self.assertEqual(floor['heldOut']['rmse'], 'UNKNOWN')
        self.assertEqual(floor['models'], {})

    def test_filled_coordinates_without_evidence_stay_unknown(self):
        document = sample()
        for point in document['floors'][0]['points']:
            point['worldEvidence'] = None
        self.assertEqual(calibrate(document)['floors'][0]['status'], 'UNKNOWN')

    def test_copied_or_self_referential_source_is_not_independent(self):
        for key in ('lineage', 'sha256'):
            document = sample()
            document['sources']['survey'][key] = document['sources']['image'][key]
            self.assertEqual(calibrate(document)['floors'][0]['acceptedFit'], 0)

    def test_calibration_annotation_is_not_independent_world_survey(self):
        document = sample()
        document['floors'][0]['calibrationSource'] = 'survey'
        self.assertEqual(calibrate(document)['floors'][0]['acceptedFit'], 0)

    def test_semantics_uncertainty_and_evidence_required(self):
        for key, value in (('method', 'projected-marker'), ('samePhysicalFeatureReviewed', False),
                           ('pickingUncertaintyWorld', .251), ('pickingUncertaintyWorld', float('nan')),
                           ('reviewRecord', ''), ('gameVersion', '')):
            document = sample()
            for point in document['floors'][0]['points']:
                point['worldEvidence'][key] = value
            self.assertEqual(calibrate(document)['floors'][0]['status'], 'UNKNOWN')

    def test_degenerate_or_single_region_split_does_not_fit(self):
        for kind in ('line', 'region'):
            document = sample()
            for i, point in enumerate(document['floors'][0]['points']):
                if kind == 'line':
                    point['image'] = [i*10, i*10]
                else:
                    point['region'] = 'only-room'
            self.assertEqual(calibrate(document)['floors'][0]['models'], {})

    def test_reject_invalid_values_duplicates_policy_override_and_outside(self):
        mutations = [lambda d: d.update(thresholds={'maxHoldoutError': 99}),
                     lambda d: d.update(schemaVersion=True),
                     lambda d: d.update(mapId='../x'),
                     lambda d: d['floors'].append(copy.deepcopy(d['floors'][0])),
                     lambda d: d['floors'][0]['points'].append(copy.deepcopy(d['floors'][0]['points'][0])),
                     lambda d: d['floors'][0]['points'][0].update(image=[float('nan'), 0]),
                     lambda d: d['floors'][0]['points'][0].update(image=[1000, 0]),
                     lambda d: d['floors'][0]['points'][0].update(world=[True, 0])]
        for mutation in mutations:
            document = sample(); mutation(document)
            with self.assertRaises(ValueError):
                calibrate(document)

    def test_json_duplicate_keys_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'input.json'
            path.write_text('{"mapId":1,"mapId":2}', encoding='utf-8')
            with self.assertRaises(ValueError):
                read_document(path)

    def test_one_floor_never_certifies_another_floor(self):
        document = sample()
        other = copy.deepcopy(document['floors'][0])
        other['floorId'] = 'Second_Level'
        for point in other['points']:
            point['world'] = None
        document['floors'].append(other)
        report = calibrate(document)
        self.assertEqual(report['floors'][0]['status'], 'NUMERIC_CRITERIA_MET_REVIEW_REQUIRED')
        self.assertEqual(report['floors'][1]['status'], 'UNKNOWN')

    def test_composition(self):
        outer, inner = (2, 3, -1, .5, 7, -2), (1, 2, 3, -1, -4, 6)
        self.assertEqual(apply(compose(outer, inner), (2, 9)), apply(outer, apply(inner, (2, 9))))

    def test_declared_lab_frames_do_not_imply_physical_calibration(self):
        source = projection([-292, -441, -96, -223], 270, [0, 0, 720, 586])
        native = projection([-287, -477, -80, -193], 270, [0, 0, 284, 207])
        transform = compose(native, inverse(source))
        self.assertAlmostEqual(transform[0], 218/720)
        self.assertAlmostEqual(transform[3], 196/586)
        self.assertAlmostEqual(transform[4], 36)
        self.assertAlmostEqual(transform[5], -5)
        self.assertAlmostEqual(-transform[5]/transform[3], 14.9489795918367)


if __name__ == '__main__':
    unittest.main()
