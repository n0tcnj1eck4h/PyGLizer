#  PyGLizer
This repository contains my attempt at making an OpenGL Loader Generator for C/C++, written in Python. If you're looking for an actual loader generator, use [glad](https://github.com/Dav1dde/glad).


Unlike [glad](https://github.com/Dav1dde/glad), this generator produces inline functions instead of `#define`'s, which allow for less awkward autocompletion in most IDE's.


The script fetches the latest [OpenGL spec](https://www.khronos.org/registry/OpenGL/xml/) from the web, parses it, and outputs two files:
- GL.h/hpp - A header containing all OpenGL types, functions and a loader. This file should be placed in the `include` directory of your project.
- GL.c/cpp - A file containing symbol definitions. Add it to your source files.
## Usage
```text
  main.py [-h] [--spec {gl,wgl,glx}] [--api {gl,gles1,gles2,glsc2}] [--profile {core,compatibility}] [--version VERSION] [--generator {cpp,c}]
               [--no-loader]
               
options:
  --spec {gl,wgl,glx}
  --api {gl,gles1,gles2,glsc2}
  --profile {core,compatibility}
  --version VERSION
  --generator {cpp,c}
  --no-loader
```
None of the arguments are required. By default, a header for the latest core version of OpenGL gets generated.

**If you're using [glfw](https://www.glfw.org/) in your project, include the GL.h/hpp header before it!**

### Example usage
```c
#include "GL.h"
#include "GLFW/glfw3.h"

int main() {
    glfwInit();
    GLFWwindow* window = glfwCreateWindow(1080, 720, "Window", NULL, NULL);
    glfwMakeContextCurrent(window);

    loadGL();
    glClearColor(1.0f, 1.0f, 0.0f, 1.0f);

    while(!glfwWindowShouldClose(window)) {
        glfwPollEvents();
        glClear(GL_COLOR_BUFFER_BIT);
        glfwSwapBuffers(window);
    }
    
    glfwTerminate();
    return 0;
}
```

## (Planned) Features / TODO's
- [x] Make it work
- [x] Separate generators for C/C++
- [ ] Write my own library handling functions (For now they are ~~stolen from~~ heavily inspired by glad)
- [ ] Typed enums
- [ ] Figure out what APIENTRY is
- [ ] Documentation generator
- [ ] Cleanup
- [ ] Debugging/Profiling stuff
- [ ] Error handing
- [ ] How do I deal with extensions
- [ ] OSX support
