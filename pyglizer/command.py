from .argument import Argument


class Command:
    def __init__(self, name: str, return_type: str, args: list[str]):
        self.name = name
        self.return_type = return_type
        self.arguments = list(map(Argument, args))
