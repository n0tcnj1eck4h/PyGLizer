# Unnamed OpenGL Loader Generator
This repository contains my attempt at making an OpenGL Loader in Python for C/C++. If you're looking for an actual loader, please use [glad](https://github.com/Dav1dde/glad).


Unlike [glad](https://github.com/Dav1dde/glad), this generator uses inline functions instead of `#define`'s, which allows for less awkward autocompletion in most IDE's.


The script downloads the lasted [OpenGL spec](https://www.khronos.org/registry/OpenGL/xml/) from the web, parses it, and outputs two files:
- GL.h - Header containing GL types, GL functions and a loader. This file should be placed in the `include` directory of your project.
- GL.cpp - File containing everything else. Add it to your source files.
## Usage
```text
./main.py -h           
usage: main.py [-h] [--api API] [--profile {core, compatibility}] [--version VERSION]

Generate an OpenGL Loader header.

options:
  -h, --help            show this help message and exit
  --api {gl, egl ...}
  --profile {core, compatibility}
  --version VERSION
```
None of the arguments are required. By default, a header for the lastest core version of OpenGL gets generated.

**If you're using [glfw](https://www.glfw.org/) in your project, include the GL.h header before it!**

TODO: EXAMPLE CODE GOES HERE 

## (Planned) Features / TODO's
- [x] Make it work
- [ ] Typed enums
- [ ] Seperate generators for C/C++
- [ ] Figure out what APIENTRY is
- [ ] Documentation generator
- [ ] Cleanup
- [ ] Debbuging/Profiling stuff
- [ ] Error handing
- [ ] How do I deal with extensions
- [ ] OSX support
