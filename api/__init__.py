
import ctypes

from fastapi import APIRouter, Request, Response, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, conint, constr

from deps import auth_required
from shared import config
from shared.locale import ErrNotFound
from shared.tools import calc_checksum

router = APIRouter(
    prefix='/api/records',
    tags=['Record'],
    dependencies=[auth_required()]
)


CheckSum = constr(min_length=32, max_length=32)


class SubmitResult(BaseModel):
    checksum: CheckSum


@router.post('/', response_model=SubmitResult)
async def record_create(request: Request, file: UploadFile):
    checksum = calc_checksum(file.file)

    file.file.seek(0)
    with open(config.records_dir / checksum, 'wb') as f:
        while chunk := file.file.read(8192):
            f.write(chunk)

    return {
        'checksum': checksum
    }


@router.delete('/{record_id}/', openapi_extra={'errors': [ErrNotFound]})
async def record_delete(request: Request, checksum: CheckSum):
    (config.records_dir / checksum).unlink(True)
    return Response(status_code=200)
