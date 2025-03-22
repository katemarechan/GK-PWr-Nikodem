#WebGl -- ostatnie zajęcie


import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
from PIL import Image

# Window dimensions
width, height = 1280, 720

# Base radius
a = 1.0

active_camera = 0
camera_rotation = 0.0
rotating = False
last_mouse_x = 0

theta = 180.0
phi = 0.0
pix2angle = 1.0
piy2angle = 1.0
R = 20.0
scale = 1.0
left_mouse_button_pressed = 0
right_mouse_button_pressed = 0
mouse_x_pos_old = 0
mouse_y_pos_old = 0
delta_x = 0
delta_y = 0
upY = 1.0



def key_callback(window, key, scancode, action, mods):
    """Handle keyboard input for camera switching and resetting."""
    global active_camera

    if action == glfw.PRESS:
        if key >= glfw.KEY_0 and key <= glfw.KEY_9:
            # Switch camera to a specific planet based on the numeric key pressed
            new_camera = key - glfw.KEY_0
            if new_camera < len(planets):
                active_camera = new_camera
        elif key == glfw.KEY_D:
            # Reset camera to default position (0th index in this case)
            active_camera = 0



def get_camera_position(time):
    """Get camera position as if standing on the orbit of the active planet."""
    planet = planets[active_camera]
    name, radius_scale, orbit_radius, _, speed_multiplier, _ = planet

    if name == "Sun":
        # For sun, maintain existing rotation around center
        camera_distance = radius_scale * 0.15
        camera_x = camera_distance * math.cos(camera_rotation)
        camera_z = camera_distance * math.sin(camera_rotation)
        return [camera_x, camera_distance, camera_z], [0, 0, 0]
    else:
        # Calculate position on planet's orbit
        angle = time * (0.02 * speed_multiplier)
        view_position = [
            orbit_radius * math.cos(angle),
            2,  # Slight elevation
            orbit_radius * math.sin(angle)
        ]

        # Calculate look direction based on mouse input
        look_x = view_position[0] + R * math.cos(2 * math.pi * theta / 360) * math.cos(2 * math.pi * phi / 360)
        look_y = view_position[1] + R * math.sin(2 * math.pi * phi / 360)
        look_z = view_position[2] + R * math.sin(2 * math.pi * theta / 360) * math.cos(2 * math.pi * phi / 360)

        look_at = [look_x, look_y, look_z]
        return view_position, look_at


def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed, right_mouse_button_pressed, mouse_x_pos_old, mouse_y_pos_old

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            left_mouse_button_pressed = 1
            x_pos, y_pos = glfw.get_cursor_pos(window)
            mouse_x_pos_old = x_pos
            mouse_y_pos_old = y_pos
        elif action == glfw.RELEASE:
            left_mouse_button_pressed = 0

    if button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            right_mouse_button_pressed = 1
            x_pos, y_pos = glfw.get_cursor_pos(window)
            mouse_x_pos_old = x_pos
        elif action == glfw.RELEASE:
            right_mouse_button_pressed = 0


def cursor_position_callback(window, x_pos, y_pos):
    global delta_x, delta_y, mouse_x_pos_old, mouse_y_pos_old, theta, phi, R

    delta_x = x_pos - mouse_x_pos_old
    delta_y = y_pos - mouse_y_pos_old
    mouse_x_pos_old = x_pos
    mouse_y_pos_old = y_pos

    if left_mouse_button_pressed:
        theta += delta_x * pix2angle
        phi += delta_y * piy2angle

    if right_mouse_button_pressed:
        if delta_x > 0 and R < 100:  # Increase upper limit for zoom-in (can zoom closer to the planets)
            R += 0.5
        elif delta_x < 0 and R > 1:  # Decrease lower limit for zoom-out (can zoom further away)
            R -= 0.5


def get_camera_position(time):
    """Get camera position based on spherical coordinates."""
    planet = planets[active_camera]
    name, radius_scale, orbit_radius, _, speed_multiplier, _ = planet

    if name == "Sun":
        planet_pos = [0, 0, 0]
    else:
        angle = time * (0.02 * speed_multiplier)
        planet_pos = [
            orbit_radius * math.cos(angle),
            0,
            orbit_radius * math.sin(angle)
        ]

    xeye = R * math.cos(2 * math.pi * theta / 360) * math.cos(2 * math.pi * phi / 360)
    yeye = R * math.sin(2 * math.pi * phi / 360)
    zeye = R * math.sin(2 * math.pi * theta / 360) * math.cos(2 * math.pi * phi / 360)

    camera_pos = [planet_pos[0] + xeye, planet_pos[1] + yeye, planet_pos[2] + zeye]

    return camera_pos, planet_pos
# Texture loading function
def load_texture(filename):
    """Load an image and convert it to a texture."""
    try:
        # Open the image
        image = Image.open(filename)

        # Ensure the file is valid
        if not image:
            raise ValueError("Image file could not be opened.")

        # Convert to RGBA
        image = image.convert("RGBA")

        # Flip the image vertically for texture wrapping
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        # Get image data
        img_data = image.tobytes()

        # Create a texture
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)

        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Upload the texture
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                     image.width, image.height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        return texture
    except FileNotFoundError:
        print(f"File not found: {filename}")
    except Exception as e:
        print(f"Error loading texture {filename}: {e}")
    return None



# Planetary data: name, radius scale, orbit radius, color, orbital speed multiplier, texture filename
planets = [
    ("Sun", a * 30, 0, (1.0, 0.8, 0.0), 0, "Sun.jpeg"),  # Bright yellow
    ("Mercury", a, 2, (0.5, 0.5, 0.5), 4.8, "Mercury.jpeg"),  # Gray
    ("Venus", a * 3, 3, (0.8, 0.6, 0.2), 3.5, "Venus.jpeg"),  # Orangish
    ("Earth", a * 3, 4, (0.0, 0.4, 0.8), 3, "Earth.jpeg"),  # Blue
    ("Mars", a * 2, 5, (0.8, 0.2, 0.0), 2.4, "Mars.jpeg"),  # Red
    ("Jupiter", a * 15, 7, (0.7, 0.5, 0.3), 1.3, "Jupiter.jpeg"),  # Brownish
    ("Saturn", a * 14, 9, (0.8, 0.7, 0.4), 1, "Saturn.jpeg"),  # Pale yellow
    ("Uranus", a * 7, 11, (0.4, 0.8, 0.9), 0.7, "Uranus.jpeg"),  # Light blue
    ("Neptune", a * 7, 13, (0.0, 0.4, 0.8), 0.5, "Neptune.jpeg")  # Deep blue
]


def init():
    """Initialize OpenGL settings with enhanced lighting."""
    glClearColor(0.0, 0.0, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)

    # Enhanced lighting properties
    ambient_light = [0.0, 0.0, 0.0, 1.0]  # Minimal ambient light
    diffuse_light = [1.0, 1.0, 1.0, 1.0]  # Bright diffuse light
    specular_light = [1.0, 1.0, 1.0, 1.0]  # White specular highlights

    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)

    # Load textures
    global planet_textures
    planet_textures = [load_texture(tex_file) for _, _, _, _, _, tex_file in planets]


def draw_sun(radius, texture):
    """Draw sun with emissive properties."""
    glDisable(GL_LIGHTING)  # Sun generates light, doesn't receive it

    # Make sun glow
    emission = [0.5, 0.4, 0.0, 1.0]
    glMaterialfv(GL_FRONT, GL_EMISSION, emission)

    if texture:
        glBindTexture(GL_TEXTURE_2D, texture)

    quadric = gluNewQuadric()
    gluQuadricTexture(quadric, GL_TRUE)
    gluSphere(quadric, radius, 50, 50)
    gluDeleteQuadric(quadric)

    # Reset emission
    glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
    glEnable(GL_LIGHTING)


def draw_orbital_path(radius):
    """Draw a white circular orbit path with transparency."""
    glDisable(GL_LIGHTING)  # Disable lighting for the orbit lines
    glColor4f(1.0, 1.0, 1.0, 0.03)  # White color with 30% opacity (alpha = 0.3)
    glLineWidth(1.0)  # Thin lines

    # Draw the orbit as a circle
    glBegin(GL_LINE_LOOP)
    for i in range(100):
        angle = 2 * math.pi * i / 100
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        glVertex3f(x, 0, z)
    glEnd()

    glEnable(GL_LIGHTING)


def draw_planet(radius, texture, rotation_angle):
    glEnable(GL_LIGHTING)

    # Enable face culling for planets
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)

    ambient = [0.2, 0.2, 0.2, 1.0]
    diffuse = [0.8, 0.8, 0.8, 1.0]
    specular = [0.2, 0.2, 0.2, 1.0]
    shininess = 50.0

    glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
    glMaterialf(GL_FRONT, GL_SHININESS, shininess)

    if texture:
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
        glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
        glEnable(GL_TEXTURE_GEN_S)
        glEnable(GL_TEXTURE_GEN_T)

    # Apply rotation around the planet's axis (Y-axis)
    glRotatef(rotation_angle, 0, 1, 0)

    quadric = gluNewQuadric()
    gluQuadricTexture(quadric, GL_TRUE)
    gluQuadricOrientation(quadric, GLU_OUTSIDE)
    gluSphere(quadric, radius, 50, 50)
    gluDeleteQuadric(quadric)

    if texture:
        glDisable(GL_TEXTURE_GEN_S)
        glDisable(GL_TEXTURE_GEN_T)

    glDisable(GL_CULL_FACE)


def draw_solar_system(time):
    """Render solar system with dynamic lighting, planet rotation, and self-rotation."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    camera_pos, look_at = get_camera_position(time)
    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              look_at[0], look_at[1], look_at[2],
              0, 1, 0)

    # Set light position at sun's center
    light_position = [0.0, 0.0, 0.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    # Draw orbital paths
    for _, _, orbit_radius, _, _, _ in planets[1:]:
        draw_orbital_path(orbit_radius)

    # Planet rotation speeds (degrees per time unit)
    # These values approximate real planet rotation periods relative to Earth
    rotation_speeds = {
        "Sun": 27,      # Sun rotates once every ~27 Earth days
        "Mercury": 59,  # Mercury rotates once every ~59 Earth days
        "Venus": -243,  # Venus has retrograde rotation (negative value)
        "Earth": 1,     # Earth's rotation period is our reference (1 day)
        "Mars": 1.03,   # Mars takes slightly longer than Earth
        "Jupiter": 0.41,# Jupiter rotates about twice as fast as Earth
        "Saturn": 0.45, # Saturn rotates about twice as fast as Earth
        "Uranus": 0.72,# Uranus rotates about 17 hours
        "Neptune": 0.67 # Neptune rotates about 16 hours
    }

    # Draw planets
    for i, (name, radius_scale, orbit_radius, color, speed_multiplier, _) in enumerate(planets):
        glPushMatrix()

        if name == "Sun":
            glColor3f(*color)
            # Calculate sun's rotation
            rotation_angle = time * 50 * rotation_speeds[name]
            draw_sun(radius_scale * 0.05, planet_textures[i])
        else:
            # Calculate orbital position
            orbital_angle = time * (0.02 * speed_multiplier)
            x = orbit_radius * math.cos(orbital_angle)
            z = orbit_radius * math.sin(orbital_angle)

            # Move to orbital position
            glTranslatef(x, 0, z)

            # Calculate self-rotation angle
            rotation_angle = time * 50 * rotation_speeds[name]

            glColor3f(*color)
            draw_planet(radius_scale * 0.05, planet_textures[i], rotation_angle)

        glPopMatrix()

def main():
    """Main function with added keyboard callback."""
    if not glfw.init():
        return

    window = glfw.create_window(width, height, "Solar System Simulation", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_key_callback(window, key_callback)  # Add keyboard callback
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_position_callback)
    glfw.set_key_callback(window, key_callback)

    # Print controls
    print(" - To show the program, readjust the window size in any way you want - ")
    print(" - To zoom in or out, use right mouse button and drag the mouse - ")
    print(" - To move the camera, use left mouse button - ")
    print(" - To place camera on Mercury: press 1 -")
    print(" - To place camera on Venus: press 2 -")
    print(" - To place camera on Earth: press 3 -")
    print(" - To place camera on Mars: press 4 -")
    print(" - To place camera on Jupiter: press 5 -")
    print(" - To place camera on Saturn: press 6 -")
    print(" - To place camera on Uranus: press 7 -")
    print(" - To place camera on Neptune: press 8 -")
    print(" - To place camera on Sun: press 0 - ")
    print(" - To return to Default camera state: press D - ")

    init()
    time = 0.0

    while not glfw.window_should_close(window):
        draw_solar_system(time)
        glfw.swap_buffers(window)
        glfw.poll_events()
        time += 0.005

    glfw.terminate()


def framebuffer_size_callback(window, w, h):
    """Adjust viewport when the window is resized."""
    global width, height
    width, height = w, h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / float(h), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


if __name__ == "__main__":
    main()