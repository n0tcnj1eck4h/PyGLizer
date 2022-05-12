#!/usr/bin/env python

import xml.etree.ElementTree as ET
from typing.io import TextIO
from SpecReader import SpecReader
import argparse
import config


def write_header(file: TextIO, spec: SpecReader):
    # Write types
    for type in spec.root.findall("./types/type"):
        file.write(ET.tostring(type, method='text', encoding='unicode').strip())
        file.write('\n')
    file.write('\n\n')  # TODO apientry

    # Write enums
    for enum in spec.required_enums:
        enum_node = spec.root.find(f"./enums/enum[@name='{enum}']")
        if enum_node is None:
            print('Failed to find', enum)
            exit()
        file.write(f'#define {enum_node.attrib["name"]} {enum_node.attrib["value"]}\n')
    file.write('\n\n')

    # Function loader declaration
    file.write('void loadGL();\n')

    for command in spec.commands:
        file.write(command.typedef())
        file.write(command.pointer_declaration())
    file.write('\n\n')

    # Write commands
    for command in spec.commands:
        file.write(command.wrapper_definition())
    file.write('\n\n')


def main():
    arg_parser = argparse.ArgumentParser(description='Generate an OpenGL Loader header.')
    arg_parser.add_argument('--api', action='store', default='gl', choices=['gl'])
    arg_parser.add_argument('--profile', action='store', default='core', choices=['core', 'compatibility'])
    arg_parser.add_argument('--version', action='store', default='latest')
    arg_parser.add_argument('--target-language', action='store', default='cpp', choices=['cpp', 'c'])
    arg_parser.add_argument('--use-typed-enums', action='store_true')
    args = arg_parser.parse_args()

    # TODO Separate version major, minor
    spec = SpecReader()

    available_apis = spec.get_apis()
    print('Available OpenGL API\'s: {}'.format(', '.join(available_apis)))

    if args.api.lower() in available_apis:
        config.API = args.api.lower()
    else:
        print('No such API exists ({})'.format(args.api))
        arg_parser.exit(0)

    print('Selected API: {}'.format(config.API))

    config.PROFILE = args.profile  # argparse already sanitizes the input
    print('Selected profile: {}'.format(config.PROFILE))

    versions = spec.get_versions(config.API)
    config.TARGET_VERSION = versions[-1] if args.version == 'latest' else \
        ([versions[0]] + [x for x in versions if x <= args.version])[-1]  # hmmm yes this is very evil

    print('Available versions for OpenGL profile {}: {}'.format(config.PROFILE, ', '.join(map(str, versions))))
    print('Selected version: {}'.format(config.TARGET_VERSION))
    if config.TARGET_VERSION not in versions:
        print("No such version exists!")
        arg_parser.exit(0)

    print('Generating loader...')
    spec.parse()

    header_file = open("GL.h", mode='w')
    header_file.write("#ifndef _WINDOWS_\n#undef APIENTRY\n#define APIENTRY\n#endif\n\n")  # whatever

    # --- Header ---
    header_file.write('#ifndef GLLLE_H\n')
    header_file.write('#define GLLLE_H\n')
    header_file.write('#define GLFW_INCLUDE_NONE\n')
    write_header(header_file, spec)
    header_file.write('#endif\n')

    header_file.close()

    # --- Implementation ---
    source_file = open("GL.cpp", mode='w')
    source_file.write('#include <GL.h>\n')
    source_file.write('#define NULL 0\n')

    with open('Sources/PlatformConfig.h') as f:
        for line in f:
            source_file.write(line)
    source_file.write('\n\n')

    with open('Sources/LibraryHandler.cpp') as f:
        for line in f:
            source_file.write(line)
    source_file.write('\n\n')

    for command in spec.commands:
        source_file.write(command.pointer_definition())
    source_file.write('\n\n')

    #for command in commands:
    #    source_file.write(command.wrapper_definition())
    #source_file.write('\n\n')

    source_file.write('void loadGL(){\n')
    source_file.write("\topen_gl();\n")
    for command in spec.commands:
        source_file.write(command.loader())
    source_file.write("\tclose_gl();\n")
    source_file.write('}\n')
    source_file.close()

    print('Done!')
    arg_parser.exit(0)


if __name__ == '__main__':
    main()
