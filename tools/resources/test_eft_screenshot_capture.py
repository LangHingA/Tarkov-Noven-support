"""Synthetic filenames/PNGs only: these tests do not certify real game captures."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from eft_screenshot_capture import new_output, parse_filename, pending_measurements, read_capture, scan

DOCUMENTED_NAME = '2026-01-03[16-20]_166.52, 17.87, 7.16_0.03673, 0.94566, -0.11506, 0.30189_14.37 (0).png'


def make_capture(directory, name=DOCUMENTED_NAME, color='red'):
    path = directory/name
    Image.new('RGB', (8, 8), color).save(path, format='PNG')
    return path


class CaptureTests(unittest.TestCase):
    def test_documented_filename_only_not_a_real_sample(self):
        result = parse_filename(DOCUMENTED_NAME)
        self.assertEqual(result['worldXYZ'], [166.52, 17.87, 7.16])
        self.assertEqual(result['originalFilename'], DOCUMENTED_NAME)
        self.assertFalse(result['nativeOriginConfirmed'])
        self.assertEqual(result['timezone'], 'UNKNOWN')

    def test_negative_and_scientific_coordinates_preserve_original(self):
        name = '2026-10-28[09-03]_-2.45E+2, -0.0, 1e-05_0, 1, -2.5e-06, 0_23.5(12).PNG'
        result = parse_filename(name)
        self.assertEqual(result['worldXYZ'], [-245, -0., .00001])
        self.assertEqual(result['originalFilename'], name)
        self.assertEqual(result['duplicateIndex'], 12)

    def test_malformed_and_noncoordinate_names_fail_closed(self):
        names = ['Screenshot.png', '../'+DOCUMENTED_NAME, 'C:\\'+DOCUMENTED_NAME,
                 DOCUMENTED_NAME.replace('[16-20]', '[24-20]'), DOCUMENTED_NAME.replace('01-03', '02-30'),
                 DOCUMENTED_NAME.replace('166.52', 'NaN'), DOCUMENTED_NAME.replace('166.52', '1e999'),
                 DOCUMENTED_NAME.replace('166.52', '1e-999'),
                 DOCUMENTED_NAME.replace('166.52', '1000001'), DOCUMENTED_NAME.replace(', ', ',\n', 1),
                 DOCUMENTED_NAME.replace('17.87, ', ''), DOCUMENTED_NAME.replace('_0.03673', '_bad'),
                 DOCUMENTED_NAME.replace('.png', '.jpg'), DOCUMENTED_NAME+'junk',
                 DOCUMENTED_NAME.replace(']_166', ']166'), DOCUMENTED_NAME.replace('2026', '２０２６')]
        for name in names:
            with self.subTest(name=name), self.assertRaises(ValueError):
                parse_filename(name)

    def test_hash_and_original_bytes_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = make_capture(root)
            before = path.read_bytes(); timestamp = path.stat().st_mtime_ns
            result = read_capture(root, path.name)
            self.assertEqual(result['screenshotSha256'], hashlib.sha256(before).hexdigest())
            self.assertEqual(result['pixelDimensions'], [8, 8])
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(path.stat().st_mtime_ns, timestamp)

    def test_corrupt_and_truncated_images_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = make_capture(root)
            path.write_bytes(path.read_bytes()[:30])
            self.assertEqual(scan(root)['captures'], [])
            self.assertEqual(len(scan(root)['rejected']), 1)

    def test_scan_does_not_recurse_and_keeps_pending_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); make_capture(root)
            (root/'nested').mkdir(); make_capture(root/'nested')
            result = scan(root)
            self.assertEqual(len(result['captures']), 1)
            pending = pending_measurements(result)
            self.assertIsNone(pending['measurements'][0]['image'])
            self.assertFalse(any(pending['measurements'][0]['confirmations'].values()))
            self.assertIn('PENDING', result['nativeCaptureAcceptance'])

    def test_missing_directory_never_created(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/'missing'
            self.assertEqual(scan(root)['status'], 'NO_SCREENSHOT_DIRECTORY')
            self.assertFalse(root.exists())

    def test_bounds_before_hashing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); make_capture(root)
            with patch('eft_screenshot_capture.MAX_FILE_BYTES', 1), self.assertRaises(ValueError):
                read_capture(root, DOCUMENTED_NAME)
            with patch('eft_screenshot_capture.MAX_FILES', 0), self.assertRaises(ValueError):
                scan(root)
            with patch('eft_screenshot_capture.MAX_TOTAL_BYTES', 1), self.assertRaises(ValueError):
                scan(root)

    def test_output_separate_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); screenshots = root/'captures'; screenshots.mkdir()
            for output in (screenshots, screenshots/'out', root):
                with self.assertRaises(ValueError):
                    new_output(output, screenshots)
            output = root/'evidence'; new_output(output, screenshots)
            with self.assertRaises(FileExistsError):
                new_output(output, screenshots)


if __name__ == '__main__':
    unittest.main()
