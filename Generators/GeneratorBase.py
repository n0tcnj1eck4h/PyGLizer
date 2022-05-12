from Types.SpecReader import SpecReader


class GeneratorBase:
    def __init__(self, spec: SpecReader):
        self.spec = spec

    def write_files(self):
        ...
