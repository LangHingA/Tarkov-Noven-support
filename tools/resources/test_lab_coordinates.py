import math
import unittest
from investigate_lab_coordinates import MODELS, apply, bounds_center, errors, fit


class CoordinateTests(unittest.TestCase):
    controls = [(-4, -2), (3, -3), (1, 5), (-3, 4)]
    held = [(6, 2), (-2, -6)]

    def check_model(self, model, expected):
        fitted = fit([(p, apply(expected, p)) for p in self.controls], model)
        residual = errors(fitted, [(p, apply(expected, p)) for p in self.held])
        self.assertLess(residual['maximum'], 1e-10)

    def test_translation(self):
        self.check_model('translation', (1, 0, 0, 1, 4, -7))

    def test_rotation(self):
        c, s = math.cos(.37), math.sin(.37)
        self.check_model('rigid', (c, -s, s, c, 4, -7))

    def test_uniform(self):
        self.check_model('uniform', (2.4, 0, 0, 2.4, 3, 8))

    def test_similarity(self):
        c, s = 1.7*math.cos(.37), 1.7*math.sin(.37)
        self.check_model('similarity', (c, -s, s, c, 4, -7))

    def test_nonuniform(self):
        self.check_model('nonuniform', (.8, 0, 0, 1.9, -5, 2))

    def test_affine(self):
        self.check_model('affine', (1.2, .3, -.2, .9, 6, -4))

    def test_reject_rank_deficient_and_unknown(self):
        for model in MODELS:
            with self.assertRaises(ValueError):
                fit([], model)
        with self.assertRaises(ValueError):
            fit([((x, x), (x, x)) for x in range(4)], 'affine')
        with self.assertRaises(ValueError):
            fit([(p, p) for p in self.controls], 'nonexistent')

    def test_held_out_mismatch_not_hidden_by_exact_training_fit(self):
        fitted = fit([(p, p) for p in self.controls[:3]], 'affine')
        self.assertAlmostEqual(errors(fitted, [((1, 1), (1, 23))])['maximum'], 22.)

    def test_extraction_volume_center_is_not_gate_threshold(self):
        region = {'outline': [dict(x=x, z=z) for x in (-190.55, -150.42) for z in (-240.06, -197.67)]}
        center = bounds_center(region)
        self.assertAlmostEqual(center[0], -170.485)
        self.assertAlmostEqual(center[1], -218.865)
        self.assertGreater(math.dist(center, (-170.66, -240.77)), 21.)


if __name__ == '__main__':
    unittest.main()
