#!/usr/bin/env python3

from Types.SpecReader import SpecReader
from os.path import exists
import requests
import argparse
import config


def download_spec():
    for file in ('gl.xml', 'wgl.xml', 'glx.xml'):
        if not exists(file):
            spec = requests.get('https://www.khronos.org/registry/OpenGL/xml/{}'.format(file))
            open(file, 'wb').write(spec.content)


def main():
    arg_parser = argparse.ArgumentParser(description='Generate an OpenGL Loader header.')
    arg_parser.add_argument('--api', action='store', default='gl', choices=['gl', 'gles1', 'gles2', 'glsc2'])
    arg_parser.add_argument('--profile', action='store', default='core', choices=['core', 'compatibility'])
    arg_parser.add_argument('--version', action='store', default='latest')
    arg_parser.add_argument('--target-language', action='store', default='cpp', choices=['cpp', 'c'])
    arg_parser.add_argument('--use-typed-enums', action='store_true')
    args = arg_parser.parse_args()

    download_spec()

    # TODO Separate version major, minor
    spec = SpecReader('gl.xml')
    spec_wgl = SpecReader('wgl.xml')
    spec_glx = SpecReader('glx.xml')

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

    spec.parse(config.API, config.TARGET_VERSION)
    #spec_wgl.parse('wgl', spec_wgl.get_versions('wgl')[-1])
    #spec_glx.parse('glx', spec_wgl.get_versions('glx')[-1])

    if args.target_language == 'cpp':
        from Generators.Cpp.Generator import Generator
        Generator(spec).write_files()
    elif args.target_language == 'c':
        from Generators.C.Generator import Generator
        Generator(spec).write_files()
    else:
        print('{} is not supported'.format(args.target_language))
        arg_parser.exit(0)

    print('Done!')
    arg_parser.exit(0)


if __name__ == '__main__':
    main()
