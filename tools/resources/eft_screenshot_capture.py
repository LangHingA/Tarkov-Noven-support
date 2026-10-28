"""Read-only EFT native screenshot inventory; no capture/input automation or network."""
import argparse
import ctypes
import datetime
import hashlib
import json
import math
import os
import re
import stat
import warnings
from pathlib import Path

from PIL import Image
from package_map import reject_reparse

MAX_FILE_BYTES = 64*1024*1024
MAX_TOTAL_BYTES = 256*1024*1024
MAX_FILES = 256
NUMBER = r'-?[0-9]{1,8}(?:\.[0-9]{1,9})?(?:[eE][+-]?[0-9]{1,3})?'
VECTOR3 = ', *'.join(f'(?P<{axis}>{NUMBER})' for axis in ('x', 'y', 'z'))
QUATERNION = ', *'.join(f'(?P<q{axis}>{NUMBER})' for axis in ('x', 'y', 'z', 'w'))
NAME = re.compile(r'(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})\[(?P<hour>[0-9]{2})-(?P<minute>[0-9]{2})\]_'
                  +VECTOR3+'_'+QUATERNION+'_'+rf'(?P<extra>{NUMBER}) *\((?P<index>[0-9]{{1,8}})\)\.png', re.ASCII | re.IGNORECASE)


def parse_filename(name):
    if not isinstance(name, str) or len(name) > 240:
        raise ValueError('unsupported native screenshot filename')
    match = NAME.fullmatch(name)
    if match is None:
        raise ValueError('unsupported native screenshot filename')
    value = match.groupdict()
    datetime.datetime.strptime(value['date']+' '+value['hour']+':'+value['minute'], '%Y-%m-%d %H:%M')
    numbers = {k: float(value[k]) for k in ('x', 'y', 'z', 'qx', 'qy', 'qz', 'qw', 'extra')}
    if any(not math.isfinite(n) or abs(n) > 1e6 for n in numbers.values()):
        raise ValueError('nonfinite/excessive filename coordinates')
    return dict(originalFilename=name, filenameFormat='eft-underscore-position-quaternion-v1',
                timestampText=value['date']+'['+value['hour']+'-'+value['minute']+']', timezone='UNKNOWN',
                worldXYZ=[numbers[a] for a in ('x', 'y', 'z')],
                quaternionXYZW=[numbers['q'+a] for a in ('x', 'y', 'z', 'w')],
                trailingScalar=numbers['extra'], duplicateIndex=int(value['index']),
                coordinateReference='UNCONFIRMED_FILENAME_POSITION', nativeOriginConfirmed=False)


def check_path(path):
    for item in (path.absolute(), *path.absolute().parents):
        if item.exists() or item.is_symlink():
            reject_reparse(item)


def native_directory():
    if os.name != 'nt':
        raise ValueError('use --directory outside Windows')
    # 只查询当前用户 Documents，不创建目录，也不扫描磁盘或其他账户。
    # Query current-user Documents without creation, disk crawling or other accounts.
    shell = ctypes.WinDLL('shell32', use_last_error=True)
    function = shell.SHGetFolderPathW
    function.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_wchar_p)
    function.restype = ctypes.c_long
    buffer = ctypes.create_unicode_buffer(32768)
    if function(None, 5, None, 0, buffer) != 0 or not buffer.value:
        raise ValueError('current user Documents lookup failed; supply --directory')
    return Path(buffer.value)/'Escape from Tarkov'/'Screenshots'


def read_capture(directory, filename):
    parsed = parse_filename(filename)
    path = directory/filename
    check_path(path)
    with path.open('rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= MAX_FILE_BYTES:
            raise ValueError('screenshot file size/type bound')
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        stream.seek(0)
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(stream) as image:
                if image.format != 'PNG' or min(image.size) <= 0 or max(image.size) > 16384 or image.width*image.height > 64*1024*1024:
                    raise ValueError('unsupported/oversized PNG')
                dimensions = list(image.size)
                image.verify()
        after = os.fstat(stream.fileno())
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise ValueError('screenshot changed while reading; retry after game finishes writing')
    return {**parsed, 'screenshotSha256': digest, 'fileBytes': before.st_size, 'pixelDimensions': dimensions,
            'evidenceStatus': 'PNG_AND_FILENAME_VALID_ORIGIN_UNCONFIRMED'}


def scan(directory):
    check_path(directory)
    result = dict(schemaVersion=1, screenshotDirectory=str(directory.absolute()),
                  nativeCaptureAcceptance='PENDING_USER_ORIGINAL_SAMPLE_REVIEW', captures=[], rejected=[])
    if not directory.exists():
        return {**result, 'status': 'NO_SCREENSHOT_DIRECTORY'}
    with os.scandir(directory) as entries:
        paths = []
        for entry in entries:
            if entry.name.lower().endswith('.png'):
                paths.append(Path(entry.path))
                if len(paths) > MAX_FILES:
                    raise ValueError('screenshot count bound; use a smaller explicit collection directory')
    if sum(p.lstat().st_size for p in paths) > MAX_TOTAL_BYTES:
        raise ValueError('collection size bound; choose a smaller collection')
    for path in sorted(paths, key=lambda p: p.name):
        try:
            result['captures'].append(read_capture(directory, path.name))
        except (ValueError, OSError, SyntaxError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
            result['rejected'].append(dict(originalFilename=path.name, reason=str(exc)))
    result['status'] = 'IMPORTABLE_RECORDS_NOT_AUTHENTICATED' if result['captures'] else 'NO_IMPORTABLE_SAMPLES'
    return result


def pending_measurements(inventory):
    # 只建待填记录；日期、文件名和哈希不能自动证明原生来源或物理对应。
    # Filename/date/hash never automatically establish native origin or physical correspondence.
    records = []
    for capture in inventory['captures']:
        records.append(dict(id='capture-'+str(len(records)+1), floorId=None, role=None, region=None,
                            originalFilename=capture['originalFilename'], screenshotSha256=capture['screenshotSha256'],
                            landmarkName=None, worldSemantic='filename-position-unconfirmed', imageSemantic=None,
                            image=None, imageSha256=None, imageLocator=None, imageSelectionMethod='manual-source-svg',
                            uncertaintyWorld=None, gameVersion=None, mode=None, sessionId=None, evidenceSource=None,
                            coordinateReferenceEvidence=None, reviewRecord=None,
                            confirmations=dict(nativeOrigin=False, mapAndFloor=False, coordinateReference=False,
                                               samePhysicalEntity=False, independentImagePick=False, independentWorldSource=False)))
    return dict(schemaVersion=1, mapId=None, measurements=records)


def new_output(output, screenshot_directory):
    check_path(output)
    target, source = output.absolute().resolve(), screenshot_directory.absolute().resolve()
    if target == source or target.is_relative_to(source) or source.is_relative_to(target):
        raise ValueError('output must be separate from the screenshot collection')
    output.mkdir(parents=True, exist_ok=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, help='Default: current Windows user Documents/Escape from Tarkov/Screenshots')
    parser.add_argument('--output', type=Path, required=True, help='New separate local evidence directory')
    args = parser.parse_args()
    directory = args.directory if args.directory is not None else native_directory()
    inventory = scan(directory)
    new_output(args.output, directory)
    for name, document in (('captures.json', inventory), ('measurements.json', pending_measurements(inventory))):
        (args.output/name).write_text(json.dumps(document, sort_keys=True, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(dict(status=inventory['status'], valid=len(inventory['captures']), rejected=len(inventory['rejected']),
                          nativeCaptureAcceptance=inventory['nativeCaptureAcceptance'])))
