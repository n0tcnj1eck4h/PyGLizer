from typing import Optional


class Enum:
    def __init__(self, name: str, value: str):
        self.name: str = name
        self.value: str = value
        self.group: Optional[str] = None
