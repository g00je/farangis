

import hashlib
from typing import IO


def calc_checksum(file: IO[bytes]) -> str:
    file.seek(0)

    result = hashlib.md5()
    while chunk := file.read(8196):
        result.update(chunk)

    return result.hexdigest()
