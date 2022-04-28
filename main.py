import xml.etree.ElementTree as ET
from typing.io import TextIO
from Command import Command

target_version = 3.3
api = "gl"
profile = "core"

internal_command_prefix = "gllle_"

# TODO types

required_enums = []
commands = []

# lul
lib_init_string = """
static void* (*getProcAddressPtr)(const char*);

#if defined(_WIN32) || defined(__CYGWIN__)
#ifndef _WINDOWS_
#undef APIENTRY
#endif
#include <windows.h>
static HMODULE libGL;

static int open_gl(void) {
    libGL = LoadLibraryW(L"opengl32.dll");
    if(libGL != NULL) {
        void (* tmp)(void);
        getProcAddressPtr = (void(*)(void)) GetProcAddress(libGL, "wglGetProcAddress");
        return getProcAddressPtr != NULL;
    }
    return 0;
}

#else
#include <dlfcn.h>
static void* libGL;

static int open_gl(void) {
    static const char *NAMES[] = {"libGL.so.1", "libGL.so"};

    unsigned int index = 0;
    for(index = 0; index < (sizeof(NAMES) / sizeof(NAMES[0])); index++) {
        libGL = dlopen(NAMES[index], RTLD_NOW | RTLD_GLOBAL);
        if(libGL != NULL) {
            getProcAddressPtr = dlsym(libGL, "glXGetProcAddressARB");
            return getProcAddressPtr != NULL;
        }
    }

    return 0;
}

#endif
"""

lib_free_string = """
#if defined(_WIN32) || defined(__CYGWIN__)

static void close_gl(void) {
    if(libGL != NULL) {
        FreeLibrary((HMODULE) libGL);
        libGL = NULL;
    }
}

#else

static void close_gl(void) {
    if(libGL != NULL) {
        dlclose(libGL);
        libGL = NULL;
    }
}

#endif
"""

loader_string = """
static void* get_proc(const char *namez) {
    void* result = NULL;
    if(libGL == NULL) return NULL;

#if !defined(__APPLE__) && !defined(__HAIKU__)
    if(getProcAddressPtr != NULL) {
        result = getProcAddressPtr(namez);
    }
#endif
    if(result == NULL) {
#if defined(_WIN32) || defined(__CYGWIN__)
        result = (void*)GetProcAddress((HMODULE) libGL, namez);
#else
        result = dlsym(libGL, namez);
#endif
    }

    return result;
}
"""


def parse(root: ET.Element):
    for feature in root.findall(f"./feature[@api='{api}']"):
        if float(feature.attrib['number']) > target_version:
            continue

        # Enums
        for requirement in feature.findall('./require/enum'):
            required_enums.append(requirement.attrib['name'])

    # Read commands
    for command_node in root.findall("./commands/command"):
        name_node = command_node.find('./proto/name')
        # Check if we require this command for target version
        if root.find(f"./feature[@api='{api}']/require/command[@name='{name_node.text}']") is None:
            continue
        type_node = command_node.find('./proto/ptype')
        return_type = type_node.text if type_node is not None else 'void'
        params = []
        for param_node in command_node.findall('./param'):
            params.append(ET.tostring(param_node, method='text', encoding='unicode').strip())
        commands.append(Command(name_node.text, return_type, params))


def write_header(file: TextIO, root):
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
    file.write('int loadGL();\n')

    # Write commands
    for command in commands:
        file.write(command.wrapper_declaration())
    file.write('\n\n')


def main():
    tree = ET.parse("gl.xml")
    root = tree.getroot()
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

    for command in commands:
        source_file.write(command.typedef())
        source_file.write(command.pointer_definition())
    source_file.write('\n\n')

    for command in commands:
        source_file.write(command.wrapper_definition())
    source_file.write('\n\n')

    # LUL
    source_file.write(lib_init_string)
    source_file.write(lib_free_string)
    source_file.write(loader_string)
    source_file.write('\n\n')

    source_file.write('int loadGL(){\n')
    source_file.write("\topen_gl();\n")
    for command in commands:
        source_file.write(command.loader())
    source_file.write("\tclose_gl();\n")
    source_file.write("\treturn 1;\n")
    source_file.write('}\n')
    source_file.close()


if __name__ == '__main__':
    main()
