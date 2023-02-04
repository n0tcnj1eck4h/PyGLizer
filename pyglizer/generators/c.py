import config
from .base import GeneratorBase
from ..command import Command
from pathlib import Path


class CGenerator(GeneratorBase):
    def write_files(self):
        self.write_header()
        self.write_sources()

    def write_header(self):
        spec_name = self.spec.spec.upper()
        file = open('{}.h'.format(spec_name), mode='w')
        file.write('#ifndef {}_H\n'.format(spec_name))
        file.write('#define {}_H\n'.format(spec_name))
        file.write('#define GLFW_INCLUDE_NONE\n')
        file.write("#ifndef _WINDOWS_\n#undef APIENTRY\n#define APIENTRY\n#endif\n\n")  # whatever
        file.write('#include <stddef.h>\n')

        for type in self.spec.types:
            file.write(type)
            file.write('\n')
        file.write('\n\n')  # TODO apientry

        # Write enums
        for enum in self.spec.enums:
            file.write(f'#define {enum.name} {enum.value}\n')
        file.write('\n\n')

        if config.GENERATE_LOADER:
            file.write('void load{}();\n'.format(spec_name))

        # Write commands
        for command in self.spec.commands:
            file.write(self.wrapper_declaration(command))
        file.write('\n\n')
        file.write('#endif\n')
        file.close()

    def write_sources(self):
        spec_name = self.spec.spec.upper()
        source_file = open('{}.c'.format(spec_name), mode='w')
        source_file.write('#include "{}.h"\n'.format(spec_name))

        with open(Path(__file__).parent / 'sources' / 'PlatformConfig.h') as f:
            for line in f:
                source_file.write(line)
        source_file.write('\n\n')

        with open(Path(__file__).parent / 'sources' / 'LibraryHandler.c') as f:
            for line in f:
                source_file.write(line)
        source_file.write('\n\n')

        for command in self.spec.commands:
            source_file.write(self.typedef(command))
            source_file.write(self.pointer_definition(command))
        source_file.write('\n\n')

        for command in self.spec.commands:
            source_file.write(self.wrapper_definition(command))
        source_file.write('\n\n')

        if config.GENERATE_LOADER:
            source_file.write('void load{}(){{\n'.format(spec_name))
            source_file.write("\topen_gl();\n")
            for command in self.spec.commands:
                source_file.write(self.loader(command))
            source_file.write("\tclose_gl();\n")
            source_file.write('}\n')

        source_file.close()

    @classmethod
    def pointer_typedef_name(cls, command: Command):
        return f'PFN{command.name.upper()}PROC'

    @classmethod
    def typedef(cls, command: Command):
        return f'typedef {command.return_type} (APIENTRY *{cls.pointer_typedef_name(command)})' + \
               f'({", ".join(map(str, command.arguments))});\n'  # apientry?

    @classmethod
    def internal_pointer_name(cls, command: Command):
        return f'{config.INTERNAL_COMMAND_PREFIX}{command.name.lower()}'

    @classmethod
    def pointer_definition(cls, command: Command):
        return f'{cls.pointer_typedef_name(command)} {cls.internal_pointer_name(command)} = NULL;\n'

    @classmethod
    def wrapper_declaration(cls, command: Command):
        return f'{command.return_type} {command.name}({", ".join(map(str, command.arguments))});\n'

    @classmethod
    def wrapper_definition(cls, command: Command):
        return f'inline {command.return_type} {command.name}({", ".join(map(str, command.arguments))})' + \
               f'{{return {cls.internal_pointer_name(command)}' + \
               f'({", ".join(list(map(lambda x: x.name, command.arguments)))});}}\n'

    @classmethod
    def loader(cls, command: Command):
        return f'\t{cls.internal_pointer_name(command)} = ' + \
               f'({cls.pointer_typedef_name(command)})get_proc("{command.name}");\n'
