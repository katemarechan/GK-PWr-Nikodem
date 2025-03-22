import sys
from glfw.GLFW import *
from OpenGL.GL import *
import numpy as np
from math import pi, sin, cos
import random

# Globals for rotation angles, drawing mode, and color toggle
rotation_x = 0.0
rotation_y = 0.0
rotation_z = 0.0
draw_mode = 0  # 0 for points, 1 for lines, 2 for triangles
show_axes = True  # Start with axes visible

n = 51
matrix = np.zeros((n + 1, n + 1, 3))
matrixColor = np.zeros((n + 1, n + 1, 3))


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)


def spin():
    glRotatef(rotation_x, 1.0, 0.0, 0.0)
    glRotatef(rotation_y, 0.0, 1.0, 0.0)
    glRotatef(rotation_z, 0.0, 0.0, 1.0)


def axes():
    glBegin(GL_LINES)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-5.0, 0.0, 0.0)
    glVertex3f(5.0, 0.0, 0.0)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -5.0, 0.0)
    glVertex3f(0.0, 5.0, 0.0)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -5.0)
    glVertex3f(0.0, 0.0, 5.0)
    glEnd()


def matrixValues():
    for i in range(0, n + 1):
        for j in range(0, n + 1):
            u = i / n
            v = j / n
            matrix[i][j][0] = (-90 * pow(u, 5) + 225 * pow(u, 4) - 270 * pow(u, 3) + 180 * pow(u, 2) - 45 * u) * cos(
                pi * v)
            matrix[i][j][1] = 160 * pow(u, 4) - 320 * pow(u, 3) + 160 * pow(u, 2)
            matrix[i][j][2] = (-90 * pow(u, 5) + 225 * pow(u, 4) - 270 * pow(u, 3) + 180 * pow(u, 2) - 45 * u) * sin(
                pi * v)


def matrixColorValues():
    for i in range(0, n + 1):
        for j in range(0, n + 1):
            matrixColor[i][j] = [random.random() for _ in range(3)]
    for i in range(0, int(n / 2) - 1):
        matrixColor[n - i][n] = matrixColor[i][0]


def render(time):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    spin()
    if show_axes:  # Only draw the axes if show_axes is True
        axes()
    if draw_mode == 0:  # Mode for points
        drawEggPoints()
    elif draw_mode == 1:  # Mode for lines
        drawEggLines()
    elif draw_mode == 2:  # Mode for triangles
        drawEggTriangles()
    elif draw_mode == 3:  # Mode for full white egg
        drawEggWhite()


def drawEggPoints():
    glColor3f(0.941, 0.917, 0.839)
    for i in range(0, n + 1):
        for j in range(0, n + 1):
            glBegin(GL_POINTS)
            glVertex3f(matrix[i][j][0], matrix[i][j][1] - 5, matrix[i][j][2])
            glEnd()


def drawEggLines():
    glColor3f(0.7, 0.2, 0.9)
    for i in range(0, n):
        for j in range(0, n):
            glBegin(GL_LINES)
            glVertex3f(matrix[i][j][0], matrix[i][j][1] - 5, matrix[i][j][2])
            glVertex3f(matrix[i + 1][j][0], matrix[i + 1][j][1] - 5, matrix[i + 1][j][2])
            glVertex3f(matrix[i][j][0], matrix[i][j][1] - 5, matrix[i][j][2])
            glVertex3f(matrix[i][j + 1][0], matrix[i][j + 1][1] - 5, matrix[i][j + 1][2])
            glEnd()


def drawEggTriangles():
    for i in range(0, n):
        for j in range(0, n):
            glBegin(GL_TRIANGLES)

            # First triangle of the square
            glColor3f(*matrixColor[i][j])
            glVertex3f(matrix[i][j][0], matrix[i][j][1] - 5, matrix[i][j][2])

            glColor3f(*matrixColor[i][j + 1])
            glVertex3f(matrix[i][j + 1][0], matrix[i][j + 1][1] - 5, matrix[i][j + 1][2])

            glColor3f(*matrixColor[i + 1][j])
            glVertex3f(matrix[i + 1][j][0], matrix[i + 1][j][1] - 5, matrix[i + 1][j][2])

            glEnd()

            glBegin(GL_TRIANGLES)

            # Second triangle of the square
            glColor3f(*matrixColor[i][j + 1])
            glVertex3f(matrix[i][j + 1][0], matrix[i][j + 1][1] - 5, matrix[i][j + 1][2])

            glColor3f(*matrixColor[i + 1][j])
            glVertex3f(matrix[i + 1][j][0], matrix[i + 1][j][1] - 5, matrix[i + 1][j][2])

            glColor3f(*matrixColor[i + 1][j + 1])
            glVertex3f(matrix[i + 1][j + 1][0], matrix[i + 1][j + 1][1] - 5, matrix[i + 1][j + 1][2])

            glEnd()


# Function to render the egg fully in white
def drawEggWhite():
    glColor3f(0.949, 0.921, 0.890)  # Set color to white
    for i in range(0, n):
        for j in range(0, n):
            glBegin(GL_TRIANGLES)

            # First triangle of the square
            glVertex3f(matrix[i][j][0], matrix[i][j][1] - 5, matrix[i][j][2])
            glVertex3f(matrix[i][j + 1][0], matrix[i][j + 1][1] - 5, matrix[i][j + 1][2])
            glVertex3f(matrix[i + 1][j][0], matrix[i + 1][j][1] - 5, matrix[i + 1][j][2])

            glEnd()

            glBegin(GL_TRIANGLES)

            # Second triangle of the square
            glVertex3f(matrix[i][j + 1][0], matrix[i][j + 1][1] - 5, matrix[i][j + 1][2])
            glVertex3f(matrix[i + 1][j][0], matrix[i + 1][j][1] - 5, matrix[i + 1][j][2])
            glVertex3f(matrix[i + 1][j + 1][0], matrix[i + 1][j + 1][1] - 5, matrix[i + 1][j + 1][2])

            glEnd()


def update_viewport(window, width, height):
    aspect_ratio = width / height if height > 0 else 1
    glMatrixMode(GL_PROJECTION)
    glViewport(0, 0, width, height)
    glLoadIdentity()
    if width <= height:
        glOrtho(-7.5, 7.5, -7.5 / aspect_ratio, 7.5 / aspect_ratio, 7.5, -7.5)
    else:
        glOrtho(-7.5 * aspect_ratio, 7.5 * aspect_ratio, -7.5, 7.5, 7.5, -7.5)
    glMatrixMode(GL_MODELVIEW)


# Callback function to handle key events
def key_callback(window, key, scancode, action, mods):
    global rotation_x, rotation_y, rotation_z, draw_mode, show_axes
    if action == GLFW_PRESS or action == GLFW_REPEAT:
        if key == GLFW_KEY_W:
            rotation_x += 5
        elif key == GLFW_KEY_S:
            rotation_x -= 5
        elif key == GLFW_KEY_A:
            rotation_y += 5
        elif key == GLFW_KEY_D:
            rotation_y -= 5
        elif key == GLFW_KEY_Q:
            rotation_z += 5
        elif key == GLFW_KEY_E:
            rotation_z -= 5
        elif key == GLFW_KEY_RIGHT:  # right arrow key for draw mode
            draw_mode = (draw_mode + 1) % 4
        elif key == GLFW_KEY_LEFT:  # left arrow key for draw mode
            draw_mode = (draw_mode - 1) % 4
        elif key == GLFW_KEY_X:
            show_axes = not show_axes


def main():
    if not glfwInit():
        sys.exit()

    window = glfwCreateWindow(400, 400, "Egg", None, None)
    if not window:
        glfwTerminate()
        sys.exit()

    glfwMakeContextCurrent(window)
    glfwSetKeyCallback(window, key_callback)
    startup()

    print("Press Arrow Left or Arrow Right to switch between modes (Points, Lines, Triangles, Full white Egg)")
    print("Press WASDQE to rotate on axes: ")
    print("Axis X: A and D")
    print("Axis Y: W and S")
    print("Axis Z: Q and E")
    print("Press X to hide the axis")


    matrixValues()
    matrixColorValues()

    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()

    glfwTerminate()


if __name__ == "__main__":
    main()
