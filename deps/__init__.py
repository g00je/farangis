
# from hashlib import sha3_512, sha256

from fastapi import Depends, Request
from fastapi.security import APIKeyHeader

from shared.errors import forbidden

token_schema = APIKeyHeader(name='Auth-Token', description='Master Token')


def auth_required():
    '''auth token is required'''

    async def decorator(request: Request, token=Depends(token_schema)):
        print(token)
        forwarded = request.headers.get('X-Forwarded-For')

        if forwarded:
            ip = forwarded.split(',')[0]
        else:
            ip = request.client.host

        print(f'{ip=}')

    dep = Depends(decorator)
    dep.errors = [forbidden]
    return dep
