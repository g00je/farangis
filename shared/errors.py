
from fastapi.responses import JSONResponse


class Error(Exception):
    def __init__(
        self, *, code: int, title: str, msg: str,
        status=400, headers={}, extra={},
    ):

        self.code = code
        self.title = title
        self.msg = msg
        self.status = status
        self.headers = headers

        if not isinstance(extra, dict):
            raise TypeError('invalid extra')

        self.extra = extra

    @property
    def schema(self):
        extra = {
            'title': 'Extra',
            'type': 'object',
            'properties': {},
        }

        for k, v in self.extra.items():
            if isinstance(v, (tuple, list)):
                t = 'array'
            elif isinstance(v, dict):
                t = 'object'
            elif isinstance(v, str):
                t = 'string'
            elif isinstance(v, (float, int)):
                t = 'number'
            elif isinstance(v, bool):
                t = 'boolean'
            else:
                t = 'any'

            extra['properties'][k] = {'type': t}

        return {
            'title': 'Error',
            'type': 'object',
            'required': ['code', 'status', 'message', 'title', 'extra'],
            'properties': {
                'code': {'type': 'integer'},
                'message': {'type': 'string'},
                'status': {'type': 'integer'},
                'title': {'type': 'string'},
                'extra': extra,
            },
            'example': {
                'code': self.code,
                'message': self.msg,
                'status': self.status,
                'title': self.title,
                'extra': self.extra,
            }
        }

    def json(self):
        return JSONResponse(
            status_code=self.status,
            content={
                'code': self.code,
                'title': self.title,
                'status': self.status,
                'message': self.msg,
                'extra': self.extra
            },
            headers=self.headers
        )

    def __call__(self, *args, **kwargs):
        msg = kwargs.pop('msg', self.msg)
        headers = kwargs.pop('headers', {})

        obj = Error(
            headers=headers,
            code=self.code,
            title=self.title,
            msg=msg.format(*args, **kwargs),
            status=self.status,
            extra=kwargs,
        )

        return obj


bad_picture = Error(
    code=40001, title='Bad Picture', msg='invalid picture file',
)
bad_verification = Error(
    code=40002, title='Bad Verification', msg='invalid verification code',
)
no_change = Error(
    code=40003, title='No Change', msg='there is nothing to change',
)
bad_auth = Error(
    code=40005, title='Bad Auth', msg='invalid authentication credentials',
    status=403
)
forbidden = Error(
    code=40006, title='Forbidden', msg='Not Enough Permissions',
    status=403
)
rate_limited = Error(
    code=40007, title='Rate Limited', msg='Too Many Requests',
    status=429
)
bad_args = Error(
    code=40009, title='Bad Args', msg='invalid args',
)
bad_gene = Error(
    code=40014, title='Bad Gene', msg='invalid {} Gene {}',
    extra={'gene': '07' * 8}
)
bad_index = Error(
    code=40015, title='Bad Index', msg='invalid {} Index {}',
    extra={'index': 8}
)
bad_page = Error(
    code=40016, title='Bad Page', msg='Page {} not found',
    extra={'page': 2}
)

database_error = Error(
    code=50001, title='Database Error', msg='Database Error',
    status=500
)


all_errors = [
    forbidden, bad_picture, bad_verification,
    no_change, bad_gene, bad_auth, rate_limited,
    bad_args, bad_index, bad_page,

    database_error
]
