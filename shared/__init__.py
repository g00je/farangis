import string
from pathlib import Path

from pydantic_settings import BaseSettings


class config:
    version: str = '1.0.0'
    lang: str = 'en'
    base_dir: Path = Path(__file__).parent.parent
    records_dir = base_dir / 'records'
    records_prefix_abc = frozenset(string.ascii_lowercase + '-0123456789')
    records_prefix_max = 32
    byte_order = 'little'


class Settings(BaseSettings):
    debug: bool = False
    farangis_api_key: str


settings = Settings(_env_file=config.base_dir / 'config/.secrets.env')


config.records_dir.mkdir(parents=True, exist_ok=True)
