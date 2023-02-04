from abc import ABC, abstractmethod
from ..specinfo import SpecInfo


class GeneratorBase(ABC):
    def __init__(self, spec: SpecInfo):
        self.spec = spec

    @abstractmethod
    def write_files(self):
        ...
