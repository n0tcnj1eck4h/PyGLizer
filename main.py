#!/usr/bin/env python

import xml.etree.ElementTree as ET
from typing.io import TextIO
from Command import Command
from os.path import exists
import argparse
import requests
import config



# TODO types

required_enums = []
commands = []


def parse(root: ET.Element):
    for feature in root.findall(f"./feature[@api='{config.API}']"):
        if float(feature.attrib['number']) > config.TARGET_VERSION:
            continue

        # Enums
        for requirement in feature.findall('./require/enum'):
            required_enums.append(requirement.attrib['name'])

    # Read commands
    for command_node in root.findall("./commands/command"):
        name_node = command_node.find('./proto/name')
        # Check if we require this command for target version
        if root.find(f"./feature[@api='{config.API}']/require/command[@name='{name_node.text}']") is None:
            continue
        type_node = command_node.find('./proto/ptype')
        return_type = type_node.text if type_node is not None else 'void'
        params = []
        for param_node in command_node.findall('./param'):
            params.append(ET.tostring(param_node, method='text', encoding='unicode').strip())
        commands.append(Command(name_node.text, return_type, params))


def write_header(file: TextIO, root: ET.Element):
    # Write types
    for type in root.findall("./types/type"):
        file.write(ET.tostring(type, method='text', encoding='unicode').strip())
        file.write('\n')
    file.write('\n\n')  # TODO apientry

    # Write enums
    for enum in required_enums:
        enum_node = root.find(f"./enums/enum[@name='{enum}']")
        if enum_node is None:
            print('Failed to find', enum)
            exit()
        file.write(f'#define {enum_node.attrib["name"]} {enum_node.attrib["value"]}\n')
    file.write('\n\n')

    # Function loader declaration
    file.write('void loadGL();\n')

    # Write commands
    for command in commands:
        file.write(command.wrapper_declaration())
    file.write('\n\n')


def download_spec():
    if not exists('gl.xml'):
        spec = requests.get('https://www.khronos.org/registry/OpenGL/xml/gl.xml')
        open('gl.xml', 'wb').write(spec.content)


def main():
    arg_parser = argparse.ArgumentParser(description='Generate an OpenGL Loader header.')
    arg_parser.add_argument('--api', action='store', default='gl', choices=['todo get apis'])
    arg_parser.add_argument('--profile', action='store', default='core', choices=['core', 'compatibility'])
    arg_parser.add_argument('--version', action='store', default='latest')
    arg_parser.add_argument('--target-language', action='store', default='cpp', choices=['cpp', 'c'])
    arg_parser.add_argument('--use-typed-enums', action='store_true')

    args = arg_parser.parse_args()
    config.API = args.api
    config.PROFILE = args.profile
    config.TARGET_VERSION = float('inf') if args.version == 'latest' else float(args.version)

    download_spec()
    root = ET.parse("gl.xml").getroot()
    parse(root)

    header_file = open("GL.h", mode='w')
    header_file.write("#ifndef _WINDOWS_\n#undef APIENTRY\n#define APIENTRY\n#endif\n\n")  # whatever

    # --- Header ---
    header_file.write('#ifndef GLLLE_H\n')
    header_file.write('#define GLLLE_H\n')
    header_file.write('#define GLFW_INCLUDE_NONE\n')
    write_header(header_file, root)
    header_file.write('#endif\n')

    header_file.close()

    # --- Implementation ---
    source_file = open("GL.cpp", mode='w')
    source_file.write('#include <GL.h>\n')

    with open('Sources/PlatformConfig.h') as f:
        for line in f:
            source_file.write(line)
    source_file.write('\n\n')

    with open('Sources/LibraryHandler.cpp') as f:
        for line in f:
            source_file.write(line)
    source_file.write('\n\n')

    for command in commands:
        source_file.write(command.typedef())
        source_file.write(command.pointer_definition())
    source_file.write('\n\n')

    for command in commands:
        source_file.write(command.wrapper_definition())
    source_file.write('\n\n')

    source_file.write('void loadGL(){\n')
    source_file.write("\topen_gl();\n")
    for command in commands:
        source_file.write(command.loader())
    source_file.write("\tclose_gl();\n")
    source_file.write('}\n')
    source_file.close()
    arg_parser.exit(0)


if __name__ == '__main__':
    main()
