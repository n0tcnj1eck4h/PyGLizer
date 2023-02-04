from typing import Literal

from pyglizer.specinfo import SpecInfo
from .base import GeneratorBase
from .c import CGenerator
from .cpp import CPPGenerator

_GENS = {
    'c' : CGenerator,
    'cpp' : CPPGenerator
    }


def get_generator(gen: Literal['c', 'cpp'], spec: SpecInfo, generate_loader: bool) -> GeneratorBase:
    return _GENS[gen](spec, generate_loader)

