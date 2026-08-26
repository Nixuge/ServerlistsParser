from dataclasses import dataclass
from typing import Optional, Type

from classes.BaseParser import BaseParser

@dataclass
class ParserMeta:
    name: str
    website: str
    version: str
    color: str
    parserClass: Type[BaseParser]
    run_bulk: bool = True
    region: Optional[str] = None