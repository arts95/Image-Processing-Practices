from tkinter import Tk
from tkinter.filedialog import askopenfilename
import sys
import dicom

try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *

except:
    print(''' ERROR: PyOpenGL not installed properly. ''')
    sys.exit()


class ImageHelper:
    def __init__(self, image):
        self.image = image
        self.loaded_pixel = self.get_pixels()

    def set_loaded_pixel(self, pixels):
        self.loaded_pixel = pixels

    def get_loaded_pixel(self):
        return self.loaded_pixel

    def get_brightness_of_pixel(self, x, y):
            return self.get_loaded_pixel()[x][y]

    def get_width(self):
        return self.image['0028', '0011'].value

    def get_height(self):
        return self.image['0028', '0010'].value

    def get_pixels(self):
        return self.image.pixel_array

    def find_min_max(self):
        array_data = []
        for row in self.get_pixels():
            for pixel in row:
                array_data.append(pixel)

        return {
            'min': min(array_data),
            'max': max(array_data)
        }

    def get_inverse(self):
        pixels = []
        for row in self.get_pixels():
            new_row = []
            for value in row:
                new_row.append(255 - value)

            pixels.append(new_row)
        self.set_loaded_pixel(pixels)
        return pixels

    def get_window_level(self):
        pixels = []
        level = 20
        window = 1000
        min_max = self.find_min_max()
        min_pixel = min_max['min']
        max_pixel = min_max['max'] / 2
        for row in self.get_pixels():
            new_row = []
            for value in row:
                if value <= level - window / 2:
                    new_value = min_pixel
                elif value > level + window / 2:
                    new_value = max_pixel
                else:
                    new_value = min_pixel + (value - level) * (max_pixel - min_pixel) / window
                new_row.append(int(new_value))

            pixels.append(new_row)
        self.set_loaded_pixel(pixels)
        return pixels


def load_textures(ih):
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    # target,level,internalformat,width,height,border,format,type,pixels
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, ih.get_width(), ih.get_height(), 0, GL_LUMINANCE, GL_UNSIGNED_BYTE,
                 ih.get_pixels())

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


def loadImage():
    global imageHelper
    Tk().withdraw()
    filename = askopenfilename()
    image = dicom.read_file(filename)
    if filename == '':
        sys.exit()
    imageHelper = ImageHelper(image)
    return imageHelper


def init():
    load_textures(imageHelper)
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)  # This Will Clear The Background Color To Black
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()  # Reset The Projection Matrix
    glMatrixMode(GL_MODELVIEW)


def display():
    glClearColor(0.0, 0.0, 0.0, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glBegin(GL_QUADS)

    glTexCoord2f(0.0, 0.0)
    glVertex2f(0.0, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0.0, imageHelper.get_width())
    glTexCoord2f(1.0, 1.0)
    glVertex2f(imageHelper.get_height(), imageHelper.get_width())
    glTexCoord2f(1.0, 0.0)
    glVertex2f(imageHelper.get_height(), 0.0)

    glEnd()
    glFlush()


def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluOrtho2D(0.0, w, 0.0, h)


def keyboard(key, x, y):
    if key == chr(27).encode():
        sys.exit(0)
    if key == b'd':
        imageHelper.set_loaded_pixel(imageHelper.get_pixels())
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, imageHelper.get_width(), imageHelper.get_height(), 0, GL_LUMINANCE,
                     GL_UNSIGNED_BYTE, imageHelper.get_pixels())
        display()
    if key == b'i':
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, imageHelper.get_width(), imageHelper.get_height(), 0, GL_LUMINANCE,
                     GL_UNSIGNED_BYTE, imageHelper.get_inverse())
        display()
    if key == b'w':
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, imageHelper.get_width(), imageHelper.get_height(), 0, GL_LUMINANCE,
                     GL_UNSIGNED_BYTE, imageHelper.get_window_level())
        display()


def move(x, y):
    text = "brightness: " + str(imageHelper.get_brightness_of_pixel(x, y))
    display()
    draw_text(text, 90, imageHelper.get_height() / 2 + 20)
    glFlush()


def draw_text(text, x, y):
    glDisable(GL_TEXTURE_2D)
    glColor3f(255, 255, 255)
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(character))
    glEnable(GL_TEXTURE_2D)


def motion(x1, y1):
    move(x1, y1)
    glFlush()


glutInit(sys.argv)
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)  # Bit mask to select a single buffered window, and RGBA mode window.
loadImage()
glutInitWindowSize(imageHelper.get_width(), imageHelper.get_height())
glutInitWindowPosition(200, 200)
glutCreateWindow('Practice 2')
init()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutPassiveMotionFunc(motion)
glutMainLoop()
