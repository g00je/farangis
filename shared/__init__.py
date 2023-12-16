import string
from pathlib import Path

from pydantic_settings import BaseSettings


class config:
    version: str = '1.0.0'
    base_dir: Path = Path(__file__).parent.parent
    records_dir = base_dir / 'records'
    records_idx: dict[int, int] = {}
    records_free: set[int] = set()
    records_prefix_abc = frozenset(string.ascii_lowercase + '-0123456789')
    records_prefix_max = 32
    api_key = ''
    byte_order = 'little'


class Settings(BaseSettings):
    debug: bool = False


settings = Settings(_env_file='.secrets')


config.records_dir.mkdir(parents=True, exist_ok=True)
