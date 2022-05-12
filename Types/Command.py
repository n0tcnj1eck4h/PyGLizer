from Types.Argument import Argument
from config import *


class Command:
    def __init__(self, name: str, return_type: str, args: list[str]):
        self.name = name
        self.return_type = return_type
        self.arguments = list(map(Argument, args))

    def pointer_typedef_name(self):
        return f'PFN{self.name.upper()}PROC'

    def typedef(self):
        return f'typedef {self.return_type} (APIENTRY *{self.pointer_typedef_name()})({ ", ".join(map(str, self.arguments))});\n'  # apientry?

    def internal_pointer_name(self):
        return f'{INTERNAL_COMMAND_PREFIX}{self.name.lower()}'

    def pointer_declaration(self):  # unused most likely
        return f'extern {self.pointer_typedef_name()} {self.internal_pointer_name()};\n'

    def pointer_definition(self):
        return f'{self.pointer_typedef_name()} {self.internal_pointer_name()} = nullptr;\n'

    def pointer_initialization(self):
        return f'{self.internal_pointer_name()} = nullptr;\n'

    def wrapper_declaration(self):  # unused due to c++ being weird about inline functions FIXME
        return f'{self.return_type} {self.name}({ ", ".join(map(str, self.arguments))});\n'

    def wrapper_definition(self):
        return f'inline {self.return_type} {self.name}({ ", ".join(map(str, self.arguments))})'\
               f'{{return {self.internal_pointer_name()}({", ".join(list(map(lambda x: x.name , self.arguments)))});}}\n'

    def loader(self):
        return f'\t{self.internal_pointer_name()} = ({self.pointer_typedef_name()})get_proc("{self.name}");\n'
