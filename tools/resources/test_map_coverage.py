import hashlib
import json
import struct
import tempfile
import unittest
from pathlib import Path
from audit_map_coverage import audit, candidate_inventory, floor_status, package_inventory, rows


class CoverageTests(unittest.TestCase):
    floor = dict(floorId='Base', order='1', nameEn='Base', nameZh='Base', abstractPath='maps/the-lab/Base.png')

    def test_missing_detail_is_not_full_floor(self):
        result = floor_status(self.floor, {}, {'kind': 'svg'}, {'maps/the-lab/base.png': 12})
        self.assertFalse(result['packageCoverage'])
        self.assertFalse(result['packagedDetail'])

    def test_files_do_not_prove_geometric_survey(self):
        result = floor_status(self.floor, {'minX': '-287'}, {'kind': 'svg'},
                              {'maps/the-lab/base.png': 12, 'maps/the-lab/base.tiles': 20})
        self.assertTrue(result['packageCoverage'])
        self.assertIn('not independently measured', result['geometricSurvey'])

    def test_checked_inventory_matches_every_native_floor(self):
        root = Path(__file__).resolve().parents[2]
        inventory = json.loads((root / 'tools/resources/map_coverage.json').read_bytes())
        maps = {r['id'] for r in rows(root / 'assets', 'map_maps.tsv')}
        floors = {(r['mapId'], r['floorId']) for r in rows(root / 'assets', 'map_floors.tsv')}
        self.assertEqual(maps, {r['mapId'] for r in inventory['maps']})
        self.assertEqual(floors, {(m['mapId'], f['floorId']) for m in inventory['maps'] for f in m['floors']})
        self.assertEqual(len(floors), inventory['floorCount'])
        self.assertFalse(next(m for m in inventory['maps'] if m['mapId'] == '68236e8153654e8c1200798a')['packageFloorCoverage'])
        for m in inventory['maps']:
            for f in m['floors']:
                self.assertNotEqual(f['sourceKind'], 'unknown')
                if f['sourceKind'] == 'tile-fallback':
                    self.assertIsNone(f['license'])

    def test_package_identity_paths_size_and_truncation(self):
        identity = b'maps.factory'
        content = b'notice'
        name = b'maps/factory/SOURCE.md'
        prefix = b'NVR1' + struct.pack('<I', len(identity)) + identity + struct.pack('<I', 1)
        raw = prefix + struct.pack('<IQ', len(name), len(content)) + name + content
        with tempfile.TemporaryDirectory(prefix='noven-coverage-') as root:
            path = Path(root) / 'test.nvr'
            def record(data, **changes):
                path.write_bytes(data)
                return dict(downloadSize=len(data), sha256=hashlib.sha256(data).hexdigest(),
                            resourceId=changes.get('identity', identity.decode()), installedSize=changes.get('size', len(content)))
            entries, _, _ = package_inventory(path, record(raw))
            self.assertEqual(entries, {'maps/factory/source.md': 6})
            for data, changes in ((raw, {'identity': 'maps.other'}), (raw, {'size': 7}),
                                  (raw[:-1], {}), (raw + b'x', {}),
                                  (prefix + struct.pack('<IQ', len(b'maps/../x.md'), 6) + b'maps/../x.md' + content, {})):
                with self.assertRaises(ValueError):
                    package_inventory(path, record(data, **changes))

    def test_empty_tutorial_is_not_vacuously_complete(self):
        with tempfile.TemporaryDirectory(prefix='noven-coverage-') as root:
            assets = Path(root)
            (assets / 'data/pve').mkdir(parents=True)
            (assets / 'maps').mkdir()
            (assets / 'data/map_maps.tsv').write_text('id\tnameEn\tnameZh\n68236e8153654e8c1200798a\tTutorial\tTutorial\n')
            for file, header in (('map_floors.tsv', 'mapId\tfloorId'), ('pve/map_floors.tsv', 'mapId\tfloorId'),
                                 ('map_references.tsv', 'mapId'), ('map_extents.tsv', 'mapId\tfloorId')):
                (assets / 'data' / file).write_text(header + '\n')
            (assets / 'maps/all.manifest.json').write_text('{"sources":[]}')
            catalog = assets / 'catalog.json'
            def catalog_with(components):
                catalog.write_text(json.dumps(dict(payloadHex=json.dumps(dict(schemaVersion=1, audience='production', components=components)).encode().hex())))
            catalog_with([])
            first = audit(assets, catalog, assets)
            self.assertEqual(first, audit(assets, catalog, assets))
            self.assertEqual(first['floorCount'], 0)
            self.assertFalse(first['maps'][0]['packageFloorCoverage'])
            self.assertEqual(first['maps'][0]['acceptanceStatus'], 'BLOCKED')
            self.assertIsNone(first['completionCount'])
            self.assertIn('Core TSVs', first['maps'][0]['nativeContractBlocker'])
            with self.assertRaises(ValueError):
                catalog_with([dict(stableMapId='unknown', resourceId='maps.unknown')])
                audit(assets, catalog, assets)

    def test_unsigned_candidate_is_separate_from_publication(self):
        identity = '68236e8153654e8c1200798a'
        content, name = b'notice', b'maps/tutorial/SOURCE.md'
        resource = ('maps.' + identity).encode()
        raw = b'NVR1' + struct.pack('<I', len(resource)) + resource + struct.pack('<I', 1)
        raw += struct.pack('<IQ', len(name), len(content)) + name + content
        with tempfile.TemporaryDirectory(prefix='noven-candidate-audit-') as root:
            root = Path(root)
            (root / 'candidate.nvr').write_bytes(raw)
            record = dict(stableMapId=identity, resourceId=resource.decode(), artifact='candidate.nvr',
                          downloadSize=len(raw), installedSize=len(content), sha256=hashlib.sha256(raw).hexdigest())
            catalog = root / 'catalog.json'
            catalog.write_text(json.dumps(dict(schemaVersion=1, components=[record])))
            result = candidate_inventory([catalog], {identity})
            self.assertEqual(result[identity][1], {'maps/tutorial/source.md': 6})
            for catalogs, ids in (([catalog, catalog], {identity}), ([catalog], {'other'})):
                with self.assertRaises(ValueError):
                    candidate_inventory(catalogs, ids)
            record['artifact'] = '../candidate.nvr'
            catalog.write_text(json.dumps(dict(schemaVersion=1, components=[record])))
            with self.assertRaisesRegex(ValueError, 'unsafe candidate artifact'):
                candidate_inventory([catalog], {identity})


if __name__ == '__main__':
    unittest.main()
