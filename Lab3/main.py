#!/usr/bin/env python3
import math
import sys
import random
from glfw.GLFW import *
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from math import *

viewer = [0.0, 0.0, 10.0]

theta = 180.0
phi = 0.0
pix2angle = 1.0
piy2angle = 1.0
pixs2angle = 1.0
scale = 1.0
R = 8.0

left_mouse_button_pressed = 0
right_mouse_button_pressed = 0
e_button_state = 1

mouse_x_pos_old = 0
mouse_y_pos_old = 0
delta_x = 0
delta_y = 0
delta_s = 0

upY = 1.0

rotation_x = 0.0
rotation_y = 0.0
rotation_z = 0.0
draw_mode = 0
color_change_enabled = False



n = 30
matrix = np.zeros((n + 1, n + 1, 3))
matrixColor = np.zeros((n + 1, n + 1, 3))


def render(time):
    global theta
    global phi
    global scale
    global R
    global upY
    global e_button_state

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    # klawisz 'e' powoduje zmiane trybu: obracanie obiektu lub tryb poruszania kamera
    if e_button_state:
        xeye = R * cos(2 * pi * theta / 360) * cos(2 * pi * phi / 360)
        yeye = R * sin(2 * pi * phi / 360)
        zeye = R * sin(2 * pi * theta / 360) * cos(2 * pi * phi / 360)

        gluLookAt(xeye, yeye, zeye, 0.0, 0.0, 0.0, 0.0, upY, 0.0)

        if phi > 180:
            phi -= 2 * 180
        elif phi <= -180:
            phi += 2 * 180

        if phi < -180 / 2 or phi > 180 / 2:
            upY = -1.0
        else:
            upY = 1

        if left_mouse_button_pressed:
            theta += delta_x * pix2angle
            phi += delta_y * piy2angle
        # 'R' moze przyjmowac wartosci od 1 do 10
        if right_mouse_button_pressed:
            if delta_x > 0 and R < 10:
                R += 0.05
            else:
                if R >= 1:
                    R -= 0.05

    else:
        gluLookAt(viewer[0], viewer[1], viewer[2], 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

        if left_mouse_button_pressed:
            theta += delta_x * pix2angle
            phi += delta_y * piy2angle

        glRotatef(theta, 0.0, 1.0, 0.0)
        glRotatef(phi, 1.0, 0.0, 0.0)

        # 'scale' moze przyjmowac wartosci od 0.3 do 3
        if right_mouse_button_pressed:
            if delta_x > 0 and scale < 3:
                scale += 0.050
            else:
                if scale >= 0.3:
                    scale -= 0.050
        glScalef(scale, scale, scale)

    axes()
    example_object()
    glFlush()


def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed
    global right_mouse_button_pressed

    if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
        left_mouse_button_pressed = 1
    else:
        left_mouse_button_pressed = 0

    if button == GLFW_MOUSE_BUTTON_RIGHT and action == GLFW_PRESS:
        right_mouse_button_pressed = 1
    else:
        right_mouse_button_pressed = 0


def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x
    global mouse_x_pos_old
    global delta_y
    global mouse_y_pos_old

    delta_x = x_pos - mouse_x_pos_old
    mouse_x_pos_old = x_pos

    delta_y = y_pos - mouse_y_pos_old
    mouse_y_pos_old = y_pos


def update_viewport(window, width, height):
    global pix2angle
    pix2angle = 360.0 / width

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(70, 1.0, 0.1, 300.0)

    if width <= height:
        glViewport(0, int((height - width) / 2), width, width)
    else:
        glViewport(int((width - height) / 2), 0, height, height)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


# Global variable to track face culling status
face_culling_enabled = False  # Initially off

def keyboard_key_callback(window, key, scancode, action, mods):
    global e_button_state, draw_mode, n, color_change_enabled, face_culling_enabled

    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    if key == GLFW_KEY_E and action == GLFW_PRESS:
        if e_button_state:
            e_button_state = 0
        else:
            e_button_state = 1
    if action == GLFW_PRESS or action == GLFW_REPEAT:
        if key == GLFW_KEY_LEFT:
            draw_mode = (draw_mode - 1) % 3
        elif key == GLFW_KEY_RIGHT:
            draw_mode = (draw_mode + 1) % 3
        elif key == GLFW_KEY_G:
            n = min(n + 6, 120)
            matrixValues()
            matrixColorValues()
        elif key == GLFW_KEY_H:
            n = max(n - 6, 6)
            matrixValues()
            matrixColorValues()
        elif key == GLFW_KEY_F and action == GLFW_PRESS:
            # Toggle face culling on/off
            face_culling_enabled = not face_culling_enabled
            if face_culling_enabled:
                glEnable(GL_CULL_FACE)
                glCullFace(GL_FRONT)  # Cull back faces
                print("Face Culling Enabled")
            else:
                glDisable(GL_CULL_FACE)
                print("Face Culling Disabled")


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)
    random.seed(1)
    matrixValues()
    matrixColorValues()
    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetKeyCallback(window, keyboard_key_callback)
    glfwSetCursorPosCallback(window, mouse_motion_callback)
    glfwSetMouseButtonCallback(window, mouse_button_callback)
    glfwSwapInterval(1)

    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()


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
    global matrix
    matrix = np.zeros((n + 1, n + 1, 3))
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
    global matrixColor
    matrixColor = np.zeros((n + 1, n + 1, 3))
    for i in range(0, n + 1):
        for j in range(0, n + 1):
            matrixColor[i][j] = [random.random() for _ in range(3)]
    for i in range(0, int(n / 2) - 1):
        matrixColor[n - i][n] = matrixColor[i][0]


def updateColor():
    if color_change_enabled:
        matrixColorValues()


def example_object():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    axes()
    updateColor()
    if draw_mode == 0:
        drawEggPoints()
    elif draw_mode == 1:
        drawEggLines()
    else:
        drawEggTriangles()
    glFlush()


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
    global n
    radiusX = 5.0
    radiusY = 5.0

    # Loop over the stacks (height) of the egg
    for i in range(n):
        y = radiusY - (2.0 * radiusY * i / n)
        yNext = radiusY - (2.0 * radiusY * (i + 1) / n)

        normalizedPosition = float(i) / float(n)
        radiusVariable = 0.7 * radiusX * sqrt(sin(pi * normalizedPosition))
        radiusVariableNext = 0.7 * radiusX * sqrt(sin(pi * (normalizedPosition + 1.0 / n)))

        glBegin(GL_TRIANGLES)

        # Use a smooth color gradient instead of random colors
        color = [0.5 + 0.5 * sin(0.1 * i), 0.5 + 0.5 * cos(0.1 * i), 1.0]  # Smooth color transition

        # Loop through all slices (360 degrees) of the egg
        for j in range(n):
            rotationNow = 2.0 * pi * float(j) / float(n)
            rotationNext = 2.0 * pi * float(j + 1) / float(n)

            # Current stack coordinates
            xNow = radiusVariable * cos(rotationNow)
            zNow = radiusVariable * sin(rotationNow)

            xNext = radiusVariable * cos(rotationNext)
            zNext = radiusVariable * sin(rotationNext)

            # Next stack coordinates
            xNowNextStack = radiusVariableNext * cos(rotationNow)
            zNowNextStack = radiusVariableNext * sin(rotationNow)

            xNextNextStack = radiusVariableNext * cos(rotationNext)
            zNextNextStack = radiusVariableNext * sin(rotationNext)

            # Set the color once per triangle strip
            glColor3f(*color)

            # Triangle 1 (between current and next stack)
            glVertex3f(xNow, y, zNow)
            glVertex3f(xNowNextStack, yNext, zNowNextStack)
            glVertex3f(xNext, y, zNext)

            # Triangle 2 (between next stack and next next stack)
            glVertex3f(xNowNextStack, yNext, zNowNextStack)
            glVertex3f(xNextNextStack, yNext, zNextNextStack)
            glVertex3f(xNext, y, zNext)

        glEnd()


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    # Enable back face culling
    glEnable(GL_CULL_FACE)
    glCullFace(GL_FRONT)  # Cull the back faces
    glFrontFace(GL_CCW)  # Set the front face winding order to counter-clockwise

    glEnable(GL_DEPTH_TEST)
    print("Press Arrow Left or Arrow Right to switch between modes (Points, Lines, Triangles) ")
    print("Use Mouse Buttons to Rotate the egg:")
    print("Left Mouse Button: Rotate the camera/egg by holding the button down")
    print("Right Mouse Button: Zoom In or Out by dragging the mouse inward or outward")
    print("Press E to change mode from Camera to Egg")
    print("Press G to increase the number of n by 6 [cap at 120]")
    print("Press H to decrease the number of n by 6 [cap at 6]")


def shutdown():
    pass


if __name__ == '__main__':
    main()

