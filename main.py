#!/usr/bin/env python

from Types.SpecReader import SpecReader
import argparse
import config


def main():
    arg_parser = argparse.ArgumentParser(description='Generate an OpenGL Loader header.')
    arg_parser.add_argument('--api', action='store', default='gl', choices=['gl', 'gles1', 'gles2', 'glsc2'])
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

    if args.target_language == 'cpp':
        from Generators.Cpp.Generator import Generator
        Generator(spec).write_files()
    else:
        print('{} is not supported'.format(args.target_language))
        arg_parser.exit(0)

    print('Done!')
    arg_parser.exit(0)


if __name__ == '__main__':
    main()
