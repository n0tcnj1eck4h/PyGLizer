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
    arg_parser.add_argument('--spec', action='store', default='gl', choices=['gl', 'wgl', 'glx'])
    arg_parser.add_argument('--api', action='store', default='gl', choices=['gl', 'gles1', 'gles2', 'glsc2'])
    arg_parser.add_argument('--profile', action='store', default='core', choices=['core', 'compatibility'])
    arg_parser.add_argument('--version', action='store', default='latest')
    arg_parser.add_argument('--generator', action='store', default='cpp', choices=['cpp', 'c'])
    arg_parser.add_argument('--no-loader', action='store_false')
    # arg_parser.add_argument('--use-typed-enums', action='store_true')
    args = arg_parser.parse_args()

    download_spec()
    config.GENERATE_LOADER = args.no_loader

    # TODO Separate version major, minor
    spec_reader = SpecReader(args.spec)

    available_apis = spec_reader.get_apis()
    print('Available OpenGL API\'s: {}'.format(', '.join(available_apis)))

    if args.spec == 'wgl':
        args.api = 'wgl'
    elif args.spec == 'glx':
        args.api = 'glx'

    config.API = args.api.lower()
    print('Selected API: {}'.format(config.API))

    config.PROFILE = args.profile
    print('Selected profile: {}'.format(config.PROFILE))

    versions = spec_reader.get_versions(config.API)
    config.TARGET_VERSION = versions[-1] if args.version == 'latest' else \
        ([versions[0]] + [x for x in versions if x <= args.version])[-1]  # hmmm yes this is very evil

    print('Available versions for OpenGL profile {}: {}'.format(config.PROFILE, ', '.join(map(str, versions))))
    print('Selected version: {}'.format(config.TARGET_VERSION))
    if config.TARGET_VERSION not in versions:
        print("No such version exists!")
        arg_parser.exit(0)

    print('Generating loader...')
    spec = spec_reader.parse(config.API, config.TARGET_VERSION)

    if args.generator == 'cpp':
        from Generators.Cpp.Generator import Generator
        Generator(spec).write_files()
    elif args.generator == 'c':
        from Generators.C.Generator import Generator
        Generator(spec).write_files()
    else:
        print('Language {} is not supported'.format(args.target_language))
        arg_parser.exit(0)

    print('Done!')
    arg_parser.exit(0)


if __name__ == '__main__':
    main()
