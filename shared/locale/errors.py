
from fastapi.responses import JSONResponse

from .langs import MessageModel, Messages, all_langs


class ErrBase(Exception):
    name: str = 'ErrBase'
    code: int = 40000
    messages = Messages()
    status: int = 400
    headers = {}
    extra: dict = None

    def __init__(self, headers: dict = None, extra: dict = None):
        if headers is not None:
            self.headers = headers

        if extra is not None:
            self.extra = extra

    @classmethod
    def schema(cls):
        scheme = {
            'title': cls.name,
            'type': 'object',
            'required': ['code', 'status', 'subject', 'content'],
            'properties': {
                'code': {'type': 'integer'},
                'status': {'type': 'integer'},
                'subject': {'type': 'string'},
                'content': {'type': 'string'},
            },
            'example': {
                'code': cls.code,
                'status': cls.status,
                **cls.messages().model_dump()
            }
        }

        if not cls.extra:
            return scheme

        extra = {
            'title': 'Extra',
            'type': 'object',
            'properties': {},
        }

        for k, v in cls.extra.items():
            if isinstance(v, str):
                t = 'string'
            elif isinstance(v, (float, int)):
                t = 'number'
            elif isinstance(v, bool):
                t = 'boolean'
            else:
                t = 'any'

            extra['properties'][k] = {'type': t}

        scheme['properties']['extra'] = extra
        scheme['required'].append('extra')
        scheme['example']['extra'] = cls.extra

        return scheme

    def json(self, lang: str = None):
        data = {
            'status': self.status,
            'code': self.code,
            **(
                self
                .messages(lang=lang)
                .format(**(self.extra or {}))
                .model_dump()
            ),
        }

        if self.extra:
            data['extra'] = self.extra

        return JSONResponse(
            status_code=self.status,
            content=data,
            headers=self.headers
        )

    def __str__(self):
        return self.messages().subject


all_errors = []


def error(code: int, name: str, status: int, extra={}) -> ErrBase:

    if 'headers' in extra:
        raise KeyError('headers cannot be an extra key')

    messages = Messages()

    for k, lang in all_langs.items():
        messages[k] = MessageModel(
            subject=lang.errors[code][0],
            content='\n'.join(lang.errors[code][1:])
        )

    err = type('Err' + name, (ErrBase, ), {
        'name': 'Err' + name,
        'code': int(code),
        'messages': messages,
        'status': status,
        'extra': extra
    })

    all_errors.append(err)

    return err


ErrBadVerification = error(40002, 'BadVerification', 403)
ErrNoChange = error(40003, 'NoChange', 400)
ErrNotFound = error(
    40004, 'NotFound', 404,
    {'item': 'Dish', 'gene': '002100abfbac001b', 'idx': 12}
)
ErrBadAuth = error(40005, 'BadAuth', 403)
ErrForbidden = error(40006, 'Forbidden', 403)
ErrRateLimited = error(40007, 'RateLimited', 429)
ErrBadArgs = error(40008, 'BadArgs', 400)
ErrBadFile = error(40009, 'BadFile', 400)
ErrDatabaseError = error(50001, 'DatabaseError', 500)
