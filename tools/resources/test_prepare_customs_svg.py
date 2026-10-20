import unittest
from pathlib import Path
from unittest.mock import patch

from prepare_customs_svg import FLOORS, MAP_ID, contract, convert, fourth_correspondence, verify_source, png, tile_pack


class CustomsSvgTests(unittest.TestCase):
    source = dict(Min=dict(x=-372, y=-306), Max=dict(x=698, y=235), rotation=180)
    target = dict(width='1070', height='544', rotation='180', minX='-372', maxX='698', minZ='-307', maxZ='237')

    def test_pins_reject_changed_source_bytes(self):
        with self.assertRaisesRegex(ValueError, 'pinned source hash mismatch'):
            verify_source('Customs-Fourth_Floor.svg', b'not the licensed pinned asset')

    def test_ground_companion_retained_and_new_floor_source_isolated(self):
        raw = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><g id="Ground_Level"><rect width="2" height="2" fill="red"/></g><g id="First_Floor"><rect x="8" y="8" width="2" height="2" fill="blue"/></g></svg>'
        source = dict(Min=dict(x=0, y=0), Max=dict(x=10, y=10), rotation=180)
        target = dict(minX=0, maxX=10, minZ=0, maxZ=10, rotation=180)
        ground = convert(raw, source, target, None, (100, 100))
        self.assertGreater(ground.getpixel((10, 10))[0], 240)
        self.assertGreater(ground.getpixel((90, 90))[2], 240)
        standalone = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><g id="Fourth_Floor"><rect x="4" y="4" width="2" height="2" fill="gold"/></g></svg>'
        fourth = convert(standalone, source, target, None, (100, 100))
        self.assertEqual(fourth.getpixel((10, 10))[3], 0)
        self.assertEqual(fourth.getpixel((90, 90))[3], 0)
        self.assertGreater(fourth.getpixel((50, 50))[3], 240)
        self.assertEqual(tile_pack(png(fourth)), tile_pack(png(convert(standalone, source, target, None, (100, 100)))))

    def test_fourth_requires_physical_region_not_ordinal_name(self):
        def svg(offset):
            return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1062.4827 535.174"><g id="Fourth_Floor">'
                    f'<path fill="gray" d="M{offset} 230h10v10h-10z"/><path fill="gray" d="M{offset} 280h10v10h-10z"/>'
                    '<rect x="430" y="230" width="1" height="1"/><rect x="430" y="280" width="1" height="1"/>'
                    '<polygon points="430,230 431,230 430,231"/></g></svg>').encode()
        report = fourth_correspondence(svg(430), self.source, self.target)
        self.assertFalse(report['independentGeometryVerified'])
        self.assertEqual(len(report['outlineWorldBounds']), 2)
        with self.assertRaisesRegex(ValueError, 'outside oilrig/panda'):
            fourth_correspondence(svg(100), self.source, self.target)

    def test_native_contract_rejects_missing_pve_floor_or_changed_height(self):
        floors = [dict(mapId=MAP_ID, floorId=f, abstractPath=f'maps/customs/{f}.png', satellitePath=f'maps/customs/{f}.satellite.png') for f in FLOORS]
        reference = dict(mapId=MAP_ID, **self.target)
        extent = dict(mapId=MAP_ID, floorId='4th_Floor', bottom='11.2', top='54.7', minX='246', maxX='279', minZ='-79', maxZ='-1.4')
        def records(assets, name):
            return [reference] if 'references' in name else [extent] if 'extents' in name else floors
        with patch('prepare_customs_svg.rows', side_effect=records):
            self.assertEqual(contract(Path('unused'))[0], reference)
        def missing(assets, name):
            return floors[:-1] if name == 'pve/map_floors.tsv' else records(assets, name)
        with patch('prepare_customs_svg.rows', side_effect=missing), self.assertRaisesRegex(ValueError, 'five-floor contract'):
            contract(Path('unused'))
        extent['bottom'] = '9.8'
        with patch('prepare_customs_svg.rows', side_effect=records), self.assertRaisesRegex(ValueError, 'fourth-floor region changed'):
            contract(Path('unused'))


if __name__ == '__main__':
    unittest.main()
