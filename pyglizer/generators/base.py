from abc import ABC, abstractmethod
from ..specinfo import SpecInfo


class GeneratorBase(ABC):
    def __init__(self, spec: SpecInfo, generate_loader: bool):
        self.spec = spec
        self.generate_loader = generate_loader

    @abstractmethod
    def write_files(self):
        ...
