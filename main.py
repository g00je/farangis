
import os
import zlib

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

import api
from shared import config, settings
from shared.locale import ErrBase, all_errors

app = FastAPI(
    title='Farangis',
    version=config.version,
    description='**Farangis api documents**',
)


app.include_router(api.router)

if settings.debug:
    app.mount('/records', StaticFiles(directory='records'), name='records')
    app.mount('/static', StaticFiles(directory='static'), name='static')


with open(config.base_dir / 'static/rapidoc.html', 'r') as f:
    RAPIDOC = f.read()


@app.exception_handler(ErrBase)
async def error_exception_handler(request, exc: ErrBase):
    return exc.json(request)


@app.on_event('startup')
async def startup():
    big = 1
    for file in config.records_dir.iterdir():
        if not file.is_file():
            continue

        idx = int.from_bytes(bytes.fromhex(file.name), config.byte_order)
        if idx > big:
            big = idx

        with open(file, 'rb') as f:
            if not f.seek(0, os.SEEK_END):
                config.records_free.add(idx)
                continue

            checksum = zlib.adler32(f.read(4096))

        config.records_idx[idx] = checksum

    config.records_idx['big'] = big


@app.on_event('shutdown')
async def shutdown():
    pass


@app.get('/rapidoc/', include_in_schema=False)
async def rapidoc():
    return HTMLResponse(RAPIDOC)


for route in app.routes:
    if not isinstance(route, APIRoute):
        continue

    errors = []

    for d in route.dependencies:
        errors.extend(getattr(d, 'errors', []))

    oid = route.path.replace('/', '_').strip('_')
    oid += '_' + '_'.join(route.methods)
    route.operation_id = oid

    errors.extend((route.openapi_extra or {}).pop('errors', []))

    for e in errors:
        route.responses[e.code] = {
            'description': f'{e.messages().subject} - {e.status}',
            'content': {
                'application/json': {
                    'schema': {
                        '$ref': f'#/errors/{e.code}',
                    }
                }
            }
        }


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    schema['errors'] = {}

    for e in all_errors:
        schema['errors'][e.code] = e.schema()

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi
