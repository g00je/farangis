
# from hashlib import sha3_512, sha256

from fastapi import Depends, Request
from fastapi.security import APIKeyHeader

from shared import settings
from shared.locale import ErrBadAuth, ErrForbidden

token_schema = APIKeyHeader(name='Authorization', description='Master Token')


def auth_required():
    '''auth token is required'''

    async def decorator(request: Request, token=Depends(token_schema)):
        if token != settings.farangis_api_key:
            raise ErrBadAuth

        forwarded = request.headers.get('X-Forwarded-For')

        if forwarded:
            ip = forwarded.split(',')[0]
        else:
            ip = request.client.host

        # TODO: use nginx to block ip's
        if ip != '127.0.0.1':
            raise ErrForbidden

    dep = Depends(decorator)
    dep.errors = [ErrBadAuth, ErrForbidden]
    return dep
