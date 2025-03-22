import sys
import random
from glfw.GLFW import *
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from math import *
from PIL import Image

viewer = [0.0, 0.0, 10.0]
theta = 180.0  # Horizontal rotation angle (in degrees)
phi = 0.0      # Vertical rotation angle (in degrees)

pix2angle = 1.0  # Horizontal mouse movement to angle conversion
piy2angle = 1.0  # Vertical mouse movement to angle conversion
pixs2angle = 1.0  # Scale adjustment factor for scrolling
R = 20.0
scale = 1.0
face_culling_enabled = True  # True = enabled, False = disabled
left_mouse_button_pressed = 0   # State of the left mouse button
right_mouse_button_pressed = 0  # State of the right mouse button
e_button_state = 1  # 1 = enabled, 0 = disabled
mouse_x_pos_old = 0  # Previous X mouse position
mouse_y_pos_old = 0  # Previous Y mouse position
delta_x = 0  # Change in mouse X position
delta_y = 0  # Change in mouse Y position
delta_s = 0  # Change in scrolling (e.g., mouse wheel)
upY = 1.0

# Rotation angles for 3D object or camera
rotation_x = 0.0  # Rotation around the X-axis
rotation_y = 0.0  # Rotation around the Y-axis
rotation_z = 0.0  # Rotation around the Z-axis

draw_mode = 0  # 0 = default mode; other values may indicate different modes

# Number of divisions for the matrix (e.g., used for a grid or surface)
n = 30

# 3D matrix to store vertex coordinates (x, y, z) for a grid of size (n+1)x(n+1)
matrix = np.zeros((n + 1, n + 1, 3))

# (u, v) coordinates for light positions in the matrix
light0_uv = [n // 3, n // 3]      # Position of the first light

texture_btn_z = 0  # Toggle between textures
image1 = Image.open("D1_t.tga")  # First texture image
image2 = Image.open("eggTxtr.tga")  # Second texture image
image3 = Image.open("cat.tga")

# Matrix for texture coordinates
matrixWithTextures = np.zeros((n + 1, n + 1, 2))
matrixWithVectors = np.zeros((n + 1, n + 1, 3))


def matrixTextures():
    """Calculate texture coordinates for the egg surface"""
    global matrixWithTextures
    # Resize the matrix based on the current value of n
    matrixWithTextures = np.zeros((n + 1, n + 1, 2))

    for i in range(0, n + 1):
        for j in range(0, n + 1):
            u = i / n
            v = j / n

            # Rotate texture on the proper half
            if i > (n / 2):
                matrixWithTextures[i][j][0] = v
                matrixWithTextures[i][j][1] = 1 - 2 * u
            else:
                matrixWithTextures[i][j][0] = v
                matrixWithTextures[i][j][1] = 2 * u

def matrixWithVectorsValues():
    """Calculate normal vectors for the egg surface"""
    global matrixWithVectors
    # Resize the matrix based on the current value of n
    matrixWithVectors = np.zeros((n + 1, n + 1, 3))

    for i in range(0, n + 1):
        for j in range(0, n + 1):
            u = i / n
            v = j / n

            xu = (-450 * pow(u, 4) + 900 * pow(u, 3) - 810 * pow(u, 2) + 360 * u - 45) * cos(pi * v)
            xv = pi * (90 * pow(u, 5) - 225 * pow(u, 4) + 270 * pow(u, 3) - 180 * pow(u, 2) + 45 * u) * sin(pi * v)
            yu = 640 * pow(u, 3) - 960 * pow(u, 2) + 320 * u
            yv = 0
            zu = (-450 * pow(u, 4) + 900 * pow(u, 3) - 810 * pow(u, 2) + 360 * u - 45) * sin(pi * v)
            zv = (- pi) * (90 * pow(u, 5) - 225 * pow(u, 4) + 270 * pow(u, 3) - 180 * pow(u, 2) + 45 * u) * cos(pi * v)

            x = yu * zv - zu * yv
            y = zu * xv - xu * zv
            z = xu * yv - yu * xv

            sum = pow(x, 2) + pow(y, 2) + pow(z, 2)
            length = sqrt(sum)

            if length > 0:
                x = x / length
                y = y / length
                z = z / length

            if i > n / 2:
                x *= -1
                y *= -1
                z *= -1

            matrixWithVectors[i][j][0] = x
            matrixWithVectors[i][j][1] = y
            matrixWithVectors[i][j][2] = z


def set_texture():
    """Set the current texture based on the toggle state"""
    if texture_btn_z == 0:
        img = image1
    elif texture_btn_z == 1:
        img = image2
    else:  # texture_btn_z == 2
        img = image3

    glTexImage2D(
        GL_TEXTURE_2D, 0, 3, img.size[0], img.size[1], 0,
        GL_RGB, GL_UNSIGNED_BYTE, img.tobytes("raw", "RGB", 0, -1)
    )

def render(time):
    global theta, phi, scale, R, upY, e_button_state

    # Clear buffers for color and depth to prepare for rendering
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if e_button_state:
        # Calculate eye position in spherical coordinates
        xeye = R * cos(2 * pi * theta / 360) * cos(2 * pi * phi / 360)
        yeye = R * sin(2 * pi * phi / 360)
        zeye = R * sin(2 * pi * theta / 360) * cos(2 * pi * phi / 360)

        # Set the camera view using gluLookAt
        gluLookAt(xeye, yeye, zeye, 0.0, 0.0, 0.0, 0.0, upY, 0.0)

        # Normalize phi to the range (-180, 180]
        if phi > 180:
            phi -= 2 * 180
        elif phi <= -180:
            phi += 2 * 180

        # Adjust the up vector based on the phi angle
        if phi < -180 / 2 or phi > 180 / 2:
            upY = -1.0
        else:
            upY = 1

        # Rotate camera based on mouse input
        if left_mouse_button_pressed:
            theta += delta_x * pix2angle
            phi += delta_y * piy2angle

        # Adjust the radius R based on mouse scroll input
        if right_mouse_button_pressed:
            if delta_x > 0 and R < 10:
                R += 0.05
            else:
                if R >= 1:
                    R -= 0.05
    else:
        # Fixed viewer position
        gluLookAt(viewer[0], viewer[1], viewer[2], 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

        # Rotate object based on mouse input
        if left_mouse_button_pressed:
            theta += delta_x * pix2angle
            phi += delta_y * piy2angle

        # Apply rotations to the object
        glRotatef(theta, 0.0, 1.0, 0.0)
        glRotatef(phi, 1.0, 0.0, 0.0)

        # Adjust object scale based on mouse scroll input
        if right_mouse_button_pressed:
            if delta_x > 0 and scale < 3:
                scale += 0.050
            else:
                if scale >= 0.3:
                    scale -= 0.050
        glScalef(scale, scale, scale)

    # Set dynamic light positions relative to the object
    set_dynamic_lights()
    axes()
    set_texture()
    example_object()  # This will now draw the textured egg
    glFlush()



def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed, right_mouse_button_pressed, mouse_x_pos_old, mouse_y_pos_old

    if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
        left_mouse_button_pressed = 1
    elif button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_RELEASE:
        left_mouse_button_pressed = 0

    if button == GLFW_MOUSE_BUTTON_RIGHT and action == GLFW_PRESS:
        right_mouse_button_pressed = 1
        # Store initial mouse position when right button is pressed
        x_pos, y_pos = glfwGetCursorPos(window)
        mouse_x_pos_old = x_pos
    elif button == GLFW_MOUSE_BUTTON_RIGHT and action == GLFW_RELEASE:
        right_mouse_button_pressed = 0

def mouse_motion(x, y, delta_x, delta_y):
    global R, right_mouse_button_pressed

    if right_mouse_button_pressed:
        # Adjust R (camera distance) based on mouse movement
        if delta_x > 0 and R < 10:
            R += 0.05  # Zoom in
        elif delta_x < 0 and R > 1:
            R -= 0.05  # Zoom out


def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x, delta_y, mouse_x_pos_old, mouse_y_pos_old, R, scale, e_button_state

    # Calculate delta movement
    delta_x = x_pos - mouse_x_pos_old
    delta_y = y_pos - mouse_y_pos_old

    # Update previous position
    mouse_x_pos_old = x_pos
    mouse_y_pos_old = y_pos

    # Zooming with right mouse button drag
    if right_mouse_button_pressed:
        if e_button_state:  # Camera mode
            # Zoom in/out based on horizontal mouse movement
            if delta_x > 0 and R < 10:
                R += 0.05  # Zoom out
            elif delta_x < 0 and R > 1:
                R -= 0.05  # Zoom in
        else:  # Object mode
            # Zoom in/out based on horizontal mouse movement
            if delta_x > 0 and scale < 3:
                scale += 0.05  # Zoom out
            elif delta_x < 0 and scale > 0.3:
                scale -= 0.05  # Zoom in


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


def keyboard_key_callback(window, key, scancode, action, mods):
    global texture_btn_z, e_button_state, n, draw_mode, R, scale, face_culling_enabled  # Declare variables as global

    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)

    # Handle zooming
    if key == GLFW_KEY_N and (action == GLFW_PRESS or action == GLFW_REPEAT):  # Zoom in
        if e_button_state:  # Camera mode
            if R > 1:
                R -= 0.05
        else:  # Object mode
            if scale < 3:
                scale += 0.05

    if key == GLFW_KEY_M and (action == GLFW_PRESS or action == GLFW_REPEAT):  # Zoom out
        if e_button_state:  # Camera mode
            if R < 10:
                R += 0.05
        else:  # Object mode
            if scale > 0.3:
                scale -= 0.05

    # Toggle face culling
    if key == GLFW_KEY_F and action == GLFW_PRESS:
        face_culling_enabled = not face_culling_enabled
        if face_culling_enabled:
            glEnable(GL_CULL_FACE)
            print("Face culling enabled")
        else:
            glDisable(GL_CULL_FACE)
            print("Face culling disabled")

    # Handle increasing/decreasing number of edges
    if key == GLFW_KEY_G and (action == GLFW_PRESS or action == GLFW_REPEAT):
        n = min(n + 6, 120)
        matrixValues()
        matrixWithVectorsValues()
        matrixTextures()

    if key == GLFW_KEY_H and (action == GLFW_PRESS or action == GLFW_REPEAT):
        n = max(n - 6, 6)
        matrixValues()
        matrixWithVectorsValues()
        matrixTextures()

    if key == GLFW_KEY_E and action == GLFW_PRESS:
        e_button_state = 1 - e_button_state  # Toggle camera/egg mode

    if action == GLFW_PRESS or action == GLFW_REPEAT:
        if key == GLFW_KEY_LEFT:
            draw_mode = (draw_mode - 1) % 3
        elif key == GLFW_KEY_RIGHT:
            draw_mode = (draw_mode + 1) % 3
    if key == GLFW_KEY_Z and action == GLFW_PRESS:
        # Cycle through 0, 1, and 2
        texture_btn_z = (texture_btn_z + 1) % 3  # 0 -> 1 -> 2 -> 01

def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)
    random.seed(1)
    matrixValues()

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetKeyCallback(window, keyboard_key_callback)
    glfwSetCursorPosCallback(window, mouse_motion_callback)
    glfwSetMouseButtonCallback(window, mouse_button_callback)
    glfwSwapInterval(1)
    matrixWithVectorsValues()
    matrixTextures()

    startup()
    # User instructions for interacting with the program
    print("> Use the mouse buttons to rotate and zoom the egg:")
    print("    Left Mouse Button [Hold]: Rotate the camera/egg by holding the button down.")
    print("    Right Mouse Button [Hold]: Zoom In or Out.")
    print("> Press E to toggle between Camera mode and Egg mode.")
    print("> Press G to increase the value of 'n' by 6 (maximum value is 120).")
    print("> Press H to decrease the value of 'n' by 6 (minimum value is 6).")
    print("> Press F to toggle face culling (enables or disables rendering of hidden surfaces).")
    print("> Press N to zoom in (Camera mode) or increase the scale (Egg mode).")
    print("> Press M to zoom out (Camera mode) or decrease the scale (Egg mode).")

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


def example_object():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    axes()

    if draw_mode == 0:
        drawEggTriangles()
    glFlush()



def drawEggTriangles():
    """Modified egg drawing with texture and normal vectors"""
    for i in range(0, n):
        for j in range(0, n):
            # Adjust front face based on egg half
            if i > (n / 2):
                glFrontFace(GL_CW)
            else:
                glFrontFace(GL_CCW)

            glBegin(GL_TRIANGLES)
            # First triangle
            glTexCoord2f(matrixWithTextures[i][j+1][0], matrixWithTextures[i][j+1][1])
            glNormal3f(matrixWithVectors[i][j+1][0], matrixWithVectors[i][j+1][1], matrixWithVectors[i][j+1][2])
            glVertex3f(matrix[i][j+1][0], matrix[i][j+1][1] - 5, matrix[i][j+1][2])

            glTexCoord2f(matrixWithTextures[i][j][0], matrixWithTextures[i][j][1])
            glNormal3f(matrixWithVectors[i][j][0], matrixWithVectors[i][j][1], matrixWithVectors[i][j][2])
            glVertex3f(matrix[i][j][0], matrix[i][j][1] - 5, matrix[i][j][2])

            glTexCoord2f(matrixWithTextures[i+1][j+1][0], matrixWithTextures[i+1][j+1][1])
            glNormal3f(matrixWithVectors[i+1][j+1][0], matrixWithVectors[i+1][j+1][1], matrixWithVectors[i+1][j+1][2])
            glVertex3f(matrix[i+1][j+1][0], matrix[i+1][j+1][1] - 5, matrix[i+1][j+1][2])
            glEnd()

            glBegin(GL_TRIANGLES)
            # Second triangle
            glTexCoord2f(matrixWithTextures[i+1][j+1][0], matrixWithTextures[i+1][j+1][1])
            glNormal3f(matrixWithVectors[i+1][j+1][0], matrixWithVectors[i+1][j+1][1], matrixWithVectors[i+1][j+1][2])
            glVertex3f(matrix[i+1][j+1][0], matrix[i+1][j+1][1] - 5, matrix[i+1][j+1][2])

            glTexCoord2f(matrixWithTextures[i][j][0], matrixWithTextures[i][j][1])
            glNormal3f(matrixWithVectors[i][j][0], matrixWithVectors[i][j][1], matrixWithVectors[i][j][2])
            glVertex3f(matrix[i][j][0], matrix[i][j][1] - 5, matrix[i][j][2])

            glTexCoord2f(matrixWithTextures[i+1][j][0], matrixWithTextures[i+1][j][1])
            glNormal3f(matrixWithVectors[i+1][j][0], matrixWithVectors[i+1][j][1], matrixWithVectors[i+1][j][2])
            glVertex3f(matrix[i+1][j][0], matrix[i+1][j][1] - 5, matrix[i+1][j][2])
            glEnd()


def configure_light(light_id, position, diffuse, constant_attenuation=0.5, linear_attenuation=0.2):
#Funkcja pomocnicza do konfiguracji światła
    glLightfv(light_id, GL_POSITION, position)
    glLightfv(light_id, GL_DIFFUSE, diffuse)
    glLightf(light_id, GL_CONSTANT_ATTENUATION, constant_attenuation)
    glLightf(light_id, GL_LINEAR_ATTENUATION, linear_attenuation)


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    # Enable texturing and related settings
    glEnable(GL_TEXTURE_2D)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Wyłączanie culling'u, aby światło mogło przejść przez obiekt
    glDisable(GL_CULL_FACE)  # Umożliwia renderowanie obu stron obiektu

    glFrontFace(GL_CCW)  # Definicja kierunku wierzchołków jako przeciwnie do ruchu wskazówek zegara

    # Włączanie oświetlenia
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Configuration of the main light source (GL_LIGHT0)
    light0_position = [3.0, 3.0, 3.0, 1.0]  # Positioned close to the object
    light0_diffuse = [0.0, 0.0, 0.0, 1.0]   # No diffuse light
    light0_ambient = [1.0, 1.0, 1.0, 1.0]   # Fully white ambient light
    light0_specular = [0.0, 0.0, 0.0, 1.0]  # No specular highlights

    glLightfv(GL_LIGHT0, GL_AMBIENT, light0_ambient)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light0_specular)
    configure_light(GL_LIGHT0, light0_position, light0_diffuse)

    # Materiał obiektu
    material_diffuse = [1.0, 1.0, 1.0, 1.0]  # White diffuse color
    material_ambient = [1.0, 1.0, 1.0, 1.0]  # White ambient color
    material_specular = [1.0, 1.0, 1.0, 1.0]  # White specular color
    material_shininess = [50.0]  # Shininess level

    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, material_diffuse)  # Use for both sides
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, material_ambient)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, material_specular)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, material_shininess)


def set_dynamic_lights():
    global matrix, light0_uv

    # Wyznaczenie pozycji światła 0
    light0_u, light0_v = light0_uv
    light0_position = [
        matrix[light0_u][light0_v][0],
        matrix[light0_u][light0_v][1] - 5,  # Adjusting Y for visibility
        matrix[light0_u][light0_v][2],
        1.0,
    ]

    # Parameters for light 0 (white color)
    light0_diffuse = [1.0, 1.0, 1.0, 1.0]  # White diffuse light
    configure_light(GL_LIGHT0, light0_position, light0_diffuse)


def shutdown():
    pass


if __name__ == '__main__':
    main()

#teksturowanie
#tekstury dwuwymiarowe
#nakleic teksture na jajko

# 3 tekstury:
# 1 strukturalnie silna skonstruwowana typu cegły
# 2 struktura slaba kulkowa(?) jako kule biljardowe
# 3 dowolna struktura ładna, strukturalna srednia
