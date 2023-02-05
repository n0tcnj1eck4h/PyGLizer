from .glenum import GLEnum
from .command import Command


class SpecInfo:
    def __init__(self, api: str, version: str, enums: list[GLEnum], commands: list[Command], types: list[str]):
        self.api: str = api
        self.enums: list[GLEnum] = enums
        self.commands: list[Command] = commands
        self.version: str = version
        self.types: list[str] = types
