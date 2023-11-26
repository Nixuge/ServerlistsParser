from dataclasses import dataclass
from typing import Type

from classes.BaseParser import BaseParser

@dataclass
class ParserMeta:
    name: str
    website: str
    version: str
    parserClass: Type[BaseParser]