#if defined(_WIN32) || defined(_WIN64) || defined(__WIN32__) || defined(__CYGWIN__) || defined(__CYGWIN32__) || defined(__TOS_WIN__) || defined(__WINDOWS__)
    #define _GL_LOADER_PLATFORM_WINDOWS
#elif defined(__unix__)
    #define _GL_LOADER_PLATFORM_UNIX
    #if defined(__linux__)
        #define _GL_LOADER_PLATFORM_LINUX
    #else
        #error Your platform is not supported
    #endif
#elif
    #error Your platform is not supported
#endif
