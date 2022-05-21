import config
from Generators.GeneratorBase import GeneratorBase
from Types.Command import Command


class Generator(GeneratorBase):
    def write_files(self):
        self.write_header()
        self.write_sources()

    def write_header(self):
        spec_name = self.spec.spec.upper()
        file = open('Output/{}.hpp'.format(spec_name), mode='w')
        file.write('#ifndef {}_H\n'.format(spec_name))
        file.write('#define {}_H\n'.format(spec_name))
        file.write('#define GLFW_INCLUDE_NONE\n')
        file.write("#ifndef _WINDOWS_\n#undef APIENTRY\n#define APIENTRY\n#endif\n\n")  # whatever

        for type in self.spec.types:
            file.write(type)  # this is stupid
            file.write('\n')
        file.write('\n\n')  # TODO apientry

        # Write enums
        for enum in self.spec.enums:
            file.write(f'#define {enum.name} {enum.value}\n')
        file.write('\n\n')

        if config.GENERATE_LOADER:
            file.write('void load{}();\n'.format(spec_name))

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
        spec_name = self.spec.spec.upper()
        source_file = open('Output/{}.cpp'.format(spec_name), mode='w')
        source_file.write('#include <{}.hpp>\n'.format(spec_name))
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

        if config.GENERATE_LOADER:
            source_file.write(f'void load{spec_name}(){{\n')
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
        return f'typedef {command.return_type} (APIENTRY *{Generator.pointer_typedef_name(command)})' + \
               f'({", ".join(map(str, command.arguments))});\n'  # apientry?

    @staticmethod
    def internal_pointer_name(command: Command):
        return f'{config.INTERNAL_COMMAND_PREFIX}{command.name.lower()}'

    @staticmethod
    def pointer_declaration(command: Command):
        return f'extern {Generator.pointer_typedef_name(command)} {Generator.internal_pointer_name(command)};\n'

    @staticmethod
    def pointer_definition(command: Command):
        return f'{Generator.pointer_typedef_name(command)} {Generator.internal_pointer_name(command)} = nullptr;\n'

    @staticmethod
    def wrapper_definition(command: Command):
        return f'inline {command.return_type} {command.name}({", ".join(map(str, command.arguments))})' + \
               f'{{return {Generator.internal_pointer_name(command)}' + \
               f'({", ".join(list(map(lambda x: x.name, command.arguments)))});}}\n'

    @staticmethod
    def loader(command: Command):
        return f'\t{Generator.internal_pointer_name(command)} = ' + \
               f'({Generator.pointer_typedef_name(command)})get_proc("{command.name}");\n'
