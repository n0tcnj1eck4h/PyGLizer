from .enum import Enum
from .command import Command


class SpecInfo:
    def __init__(self, spec, enums, commands, api, version, types):
        self.spec: str = spec
        self.enums: list[Enum] = enums
        self.commands: list[Command] = commands
        self.api: str = api
        self.version: str = version
        self.types: list[str] = types
