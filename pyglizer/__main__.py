#!/usr/bin/env python3

from pathlib import Path
from typing import Literal
from .generators import get_generator
from .specparser import SpecParser
from os.path import exists
import requests
import argparse


def download_spec(spec: Literal['gl', 'wgl', 'glx']):
    filename = Path(__file__).parent / 'cache' / (spec + '.xml')
    if not exists(filename):
        res = requests.get('https://www.khronos.org/registry/OpenGL/xml/{}.xml'.format(spec))
        open(filename, 'wb').write(res.content)
    return open(filename, 'r')


arg_parser = argparse.ArgumentParser(description='Generate an OpenGL Loader header.')
arg_parser.add_argument('--spec', action='store', default='gl', choices=['gl', 'wgl', 'glx'])
arg_parser.add_argument('--api', action='store', default='gl', choices=['gl', 'gles1', 'gles2', 'glsc2'])
arg_parser.add_argument('--profile', action='store', default='core', choices=['core', 'compatibility'])
arg_parser.add_argument('--version', action='store', default='latest')
arg_parser.add_argument('--generator', action='store', default='cpp', choices=['cpp', 'c'])
arg_parser.add_argument('--no-loader', action='store_true')
# arg_parser.add_argument('--use-typed-enums', action='store_true')
args = arg_parser.parse_args()

# only the gl spec has an api choice
if args.spec != 'gl':
    args.api = args.spec

parser = SpecParser(download_spec(args.spec))
apis = parser.get_apis()
versions = parser.get_versions(args.api)

version = versions[-1] if args.version == 'latest' else \
    ([versions[0]] + [x for x in versions if x <= args.version])[-1]  # hmmm yes this is very evil

if version not in versions:
    print("No such version exists!")
    arg_parser.exit(1)

print('Available OpenGL API\'s: {}'.format(', '.join(apis)))
print('Selected API: {}'.format(args.api))
print('Selected profile: {}'.format(args.profile))
print('Available versions for OpenGL {} profile: {}'.format(args.profile, ', '.join(versions)))
print('Selected version: {}'.format(version))
print('Generating loader...')

spec_info = parser.parse(args.api, version)
get_generator(args.generator, spec_info, not args.no_loader).write_files()

print('Done!')
arg_parser.exit(0)


