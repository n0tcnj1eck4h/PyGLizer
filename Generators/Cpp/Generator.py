import config
from Generators.GeneratorBase import GeneratorBase
import xml.etree.ElementTree as ET
from Types.Command import Command


class Generator(GeneratorBase):
    def write_files(self):
        self.write_header()
        self.write_sources()

    def write_header(self):
        file = open("Output/GL.hpp", mode='w')
        file.write('#ifndef GLLLE_H\n')
        file.write('#define GLLLE_H\n')
        file.write('#define GLFW_INCLUDE_NONE\n')
        file.write("#ifndef _WINDOWS_\n#undef APIENTRY\n#define APIENTRY\n#endif\n\n")  # whatever

        for type in self.spec.root.findall("./types/type"):
            file.write(ET.tostring(type, method='text', encoding='unicode').strip())  # this is stupid
            file.write('\n')
        file.write('\n\n')  # TODO apientry

        # Write enums
        for enum in self.spec.enums:
            file.write(f'#define {enum.name} {enum.value}\n')
        file.write('\n\n')

        # Function loader declaration
        file.write('void loadGL();\n')

        for command in self.spec.commands:
            file.write(self.typedef(command))
            file.write(self.pointer_declaration(command))
        file.write('\n\n')

        # Write commands
        for command in self.spec.commands:
            file.write(self.wrapper_definition(command))
        file.write('\n\n')
        file.write('#endif\n')
        file.close()

    def write_sources(self):
        source_file = open("Output/GL.cpp", mode='w')
        source_file.write('#include <GL.hpp>\n')
        source_file.write('#define NULL 0\n')

        with open('Sources/PlatformConfig.h') as f:
            for line in f:
                source_file.write(line)
        source_file.write('\n\n')

        with open('Sources/LibraryHandler.cpp') as f:
            for line in f:
                source_file.write(line)
        source_file.write('\n\n')

        for command in self.spec.commands:
            source_file.write(self.pointer_definition(command))
        source_file.write('\n\n')

        source_file.write('void loadGL(){\n')
        source_file.write("\topen_gl();\n")
        for command in self.spec.commands:
            source_file.write(self.loader(command))
        source_file.write("\tclose_gl();\n")
        source_file.write('}\n')
        source_file.close()

    # everything below this line is absolutely unhinged
    @staticmethod
    def pointer_typedef_name(command: Command):
        return f'PFN{command.name.upper()}PROC'

    @staticmethod
    def typedef(command: Command):
        return f'typedef {command.return_type} (APIENTRY *{Generator.pointer_typedef_name(command)})\
        ({", ".join(map(str, command.arguments))});\n'  # apientry?

    @staticmethod
    def internal_pointer_name(command: Command):
        return f'{config.INTERNAL_COMMAND_PREFIX}{command.name.lower()}'

    @staticmethod
    def pointer_declaration(command: Command):  # unused most likely
        return f'extern {Generator.pointer_typedef_name(command)} {Generator.internal_pointer_name(command)};\n'

    @staticmethod
    def pointer_definition(command: Command):
        return f'{Generator.pointer_typedef_name(command)} {Generator.internal_pointer_name(command)} = nullptr;\n'

    @staticmethod
    def pointer_initialization(command: Command):
        return f'{Generator.internal_pointer_name(command)} = nullptr;\n'

    @staticmethod
    def wrapper_definition(command: Command):
        return f'inline {command.return_type} {command.name}({", ".join(map(str, command.arguments))})' \
               f'{{return {Generator.internal_pointer_name(command)}\
               ({", ".join(list(map(lambda x: x.name, command.arguments)))});}}\n'

    @staticmethod
    def loader(command: Command):
        return f'\t{Generator.internal_pointer_name(command)} = \
        ({Generator.pointer_typedef_name(command)})get_proc("{command.name}");\n'
