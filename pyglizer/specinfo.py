from .enum import Enum
from .command import Command


class SpecInfo:
    def __init__(self, api: str, version: str, enums: list[Enum], commands: list[Command], types: list[str]):
        self.api: str = api
        self.enums: list[Enum] = enums
        self.commands: list[Command] = commands
        self.version: str = version
        self.types: list[str] = types
