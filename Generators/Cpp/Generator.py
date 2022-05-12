from Generators.GeneratorBase import GeneratorBase
import xml.etree.ElementTree as ET


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
            file.write(command.typedef())
            file.write(command.pointer_declaration())
        file.write('\n\n')

        # Write commands
        for command in self.spec.commands:
            file.write(command.wrapper_definition())
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
            source_file.write(command.pointer_definition())
        source_file.write('\n\n')

        source_file.write('void loadGL(){\n')
        source_file.write("\topen_gl();\n")
        for command in self.spec.commands:
            source_file.write(command.loader())
        source_file.write("\tclose_gl();\n")
        source_file.write('}\n')
        source_file.close()

