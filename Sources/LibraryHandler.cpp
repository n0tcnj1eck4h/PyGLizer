static void* (*getProcAddressPtr)(const char*);
#ifdef _GL_LOADER_PLATFORM_WINDOWS
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
#else // Unix
#include <dlfcn.h>
static void* libGL;
static int open_gl(void) {
    static const char *NAMES[] = {"libGL.so.1", "libGL.so"};
    for(int i = 0; i < (sizeof(NAMES) / sizeof(NAMES[0])); i++) {
        libGL = dlopen(NAMES[i], RTLD_NOW | RTLD_GLOBAL);
        if(libGL != NULL) {
            getProcAddressPtr = dlsym(libGL, "glXGetProcAddressARB");
            return getProcAddressPtr != NULL;
        }
    }
    return 0;
}
#endif

// Close
#ifdef _GL_LOADER_PLATFORM_WINDOWS
static void close_gl(void) {
    if(libGL != NULL) {
        FreeLibrary(libGL);
        libGL = NULL;
    }
}
#else //Unix
static void close_gl(void) {
    if(libGL != NULL) {
        dlclose(libGL);
        libGL = NULL;
    }
}
#endif

// Loader
static void* get_proc(const char *namez) {
    void* result = NULL;
    if(libGL == NULL) return NULL;

    if(getProcAddressPtr != NULL) {
        result = getProcAddressPtr(namez);
    }
    if(result == NULL) {
#if _GL_LOADER_PLATFORM_WINDOWS
        result = (void*)GetProcAddress((HMODULE) libGL, namez);
#else
        result = dlsym(libGL, namez);
#endif
    }

    return result;
}
