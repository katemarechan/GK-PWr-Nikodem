import sys
import random
from glfw.GLFW import *
from OpenGL.GL import *

# Set up the dark gray color for the window with the size 2187 x 2187 pixels [2187 because nicely divided by 3]
def startup():
    update_viewport(None, 2187, 2187)
    glClearColor(0.07, 0.086, 0.098, 0.0)  # Set background to black for main square

# Close the program when finished
def shutdown():
    pass

# Dictionary to store random colors for each "deleted" square, keyed by position and depth
deleted_square_colors = {}

# Draw a single square at a specific position and with a given size
# If color is specified, it is used; otherwise, the square is drawn in black
def draw_square(x, y, size, color=None):
    if color:
        glColor3f(*color)  # Use provided color for the "deleted" square
    else:
        glColor3f(0.0, 0.0, 0.0)  # Default black color for the main square

    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + size, y)
    glVertex2f(x + size, y + size)
    glVertex2f(x, y + size)
    glEnd()

# Recursively draw the Sierpiński carpet pattern
def drawFractal(x, y, size, depth):
    # Base case: if depth is 0, draw a single black square
    if depth == 0:
        draw_square(x, y, size)
    else:
        # Calculate the size of each sub-square by dividing by 3
        new_size = size / 3
        for i in range(3):
            for j in range(3):
                # Skip the center square (this is the "deleted" square)
                if i == 1 and j == 1:
                    # Generate a unique key for this square's position and recursion depth
                    key = (x + new_size * i, y + new_size * j, depth)
                    # If the square doesn't already have a color, assign a random color
                    if key not in deleted_square_colors:
                        deleted_square_colors[key] = (random.random(), random.random(), random.random())
                    # Retrieve the color from the dictionary and use it to draw the "deleted" square
                    color = deleted_square_colors[key]
                    draw_square(x + new_size * i, y + new_size * j, new_size, color=color)
                else:
                    # Recursively draw smaller squares for each non-center position
                    drawFractal(x + new_size * i, y + new_size * j, new_size, depth - 1)

# Render function to clear the screen and start drawing the fractal pattern
def render(time):
    glClear(GL_COLOR_BUFFER_BIT)
    # Begin drawing the carpet from the center with the initial size and recursion depth
    drawFractal(-1093.5, -1093.5, 2187, 4)  # Start at (-1093.5, -1093.5) to center the 2187 square
    glFlush()

# Handle window resizing and maintain the correct aspect ratio
def update_viewport(window, width, height):
    if width == 0:
        width = 1
    if height == 0:
        height = 1
    aspect_ratio = width / height

    glMatrixMode(GL_PROJECTION)
    glViewport(0, 0, width, height)
    glLoadIdentity()

    if width <= height:
        glOrtho(-1093.5, 1093.5, -1093.5 / aspect_ratio, 1093.5 / aspect_ratio, 1.0, -1.0)
    else:
        glOrtho(-1093.5 * aspect_ratio, 1093.5 * aspect_ratio, -1093.5, 1093.5, 1.0, -1.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

# Main function to initialize GLFW, set up the window, and begin the rendering loop
def main():
    if not glfwInit():
        sys.exit(-1)

    # Set up the window with 2187 x 2187 size to match the fractal dimensions
    window = glfwCreateWindow(2187, 2187, "Sierpiński Carpet", None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSwapInterval(1)

    # Initialize OpenGL settings and begin the render loop
    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()

if __name__ == '__main__':
    main()
