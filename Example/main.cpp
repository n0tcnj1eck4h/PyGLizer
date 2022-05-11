#include "../GL.h"
#include "GLFW/glfw3.h"

int main() {
    glfwInit();

    GLFWwindow* window = glfwCreateWindow(1080, 720, "Window", NULL, NULL);

    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);

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