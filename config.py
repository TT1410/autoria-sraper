import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Setting:
    DATABASE_URL: str = os.environ.get("DATABASE_URL")
