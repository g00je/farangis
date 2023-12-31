

import ctypes
import zlib

from fastapi import APIRouter, Request, Response, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, conint

from deps import auth_required
from shared import config
from shared.locale import ErrNotFound

router = APIRouter(
    prefix='/api/records',
    tags=['Record'],
    dependencies=[auth_required()]
)


class Record(ctypes.Structure):
    _fields_ = [
        ('id', ctypes.c_uint32),
        ('hash', ctypes.c_uint32)
    ]


RecordId = conint(gt=0, lt=1 << 32)
CheckSum = conint(gt=0, lt=1 << 32)


class SubmitResult(BaseModel):
    id: RecordId
    checksum: CheckSum


@router.post('/', response_model=SubmitResult)
async def record_create(request: Request, file: UploadFile):
    idx = 0
    if config.records_free:
        idx = config.records_free.pop()
        if idx > config.records_idx.get('big', 1):
            config.records_idx['big'] = idx + 1
    else:
        idx = config.records_idx.get('big', 1)
        config.records_idx['big'] = idx + 1

    filename = idx.to_bytes(4, byteorder=config.byte_order).hex()
    checksum = zlib.adler32(file.file.read(4096))
    file.file.seek(0)

    with open(config.records_dir / filename, 'wb') as f:
        while chunk := file.file.read(8192):
            f.write(chunk)

    return {
        'id': idx,
        'checksum': checksum
    }


@router.delete('/{record_id}/', openapi_extra={'errors': [ErrNotFound]})
async def record_delete(request: Request, record_id: RecordId):

    filename = record_id.to_bytes(4, byteorder=config.byte_order).hex()
    config.records_idx.pop(record_id, None)
    config.records_free.add(record_id)

    path = config.records_dir / filename
    if not path.is_file():
        raise ErrNotFound

    # write 0 bytes to the file
    open(path, 'wb').close()

    return Response(status_code=200)


@router.put(
    '/{record_id}/', response_model=SubmitResult,
    openapi_extra={'errors': [ErrNotFound]}
)
async def record_replace(request: Request, record_id: RecordId, file: UploadFile):

    if (
        record_id not in config.records_idx and
        record_id not in config.records_free
    ):
        raise ErrNotFound

    filename = record_id.to_bytes(4, byteorder=config.byte_order).hex()

    if record_id > config.records_idx.get('big', 1):
        config.records_idx['big'] = record_id + 1

    if record_id in config.records_free:
        config.records_free.remove(record_id)

    checksum = zlib.adler32(file.file.read(4096))
    file.file.seek(0)
    config.records_idx[record_id] = checksum

    with open(config.records_dir / filename, 'wb') as f:
        while chunk := file.file.read(8192):
            f.write(chunk)

    return {
        'id': record_id,
        'checksum': checksum
    }


@router.get(
    '/{record_id}/', response_class=FileResponse,
    openapi_extra={'errors': [ErrNotFound]}
)
async def record_get(request: Request, record_id: RecordId):
    filename = record_id.to_bytes(4, byteorder=config.byte_order).hex()
    path = config.records_dir / filename

    if record_id in config.records_free or not path.is_file():
        raise ErrNotFound

    checksum = str(config.records_idx.get(record_id, ''))
    return FileResponse(path, headers={'x-checksum': checksum})
