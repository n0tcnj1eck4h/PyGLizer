from abc import ABC, abstractmethod
from ..spec import Spec


class GeneratorBase(ABC):
    def __init__(self, spec: Spec):
        self.spec = spec

    @abstractmethod
    def write_files(self):
        ...
