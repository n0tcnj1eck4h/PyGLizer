from Types.Spec import Spec


class GeneratorBase:
    def __init__(self, spec: Spec):
        self.spec = spec

    def write_files(self):
        ...
