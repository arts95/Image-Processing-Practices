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

    def get_image_with_bit_map(self):
        pixels = []
        middle = self.get_width() / 2
        for row in self.get_pixels():
            new_row = []
            for index, pixel in enumerate(row):
                new_row.append(int(index > middle) and pixel)
            pixels.append(new_row)

        return pixels

    def get_gradient(self):
        min_max = self.find_min_max()
        red_gradient = {}
        red = 255
        for key in range(min_max['min'], min_max['max'] + 1):
            red_gradient[key] = red
            red -= 1

        return red_gradient

    def get_red_image(self):
        pixels = []
        red_gradient = self.get_gradient()
        for row in self.get_pixels():
            new_row = []
            for value in row:
                new_row.append([red_gradient[value], 0, 0])

            pixels.append(new_row)

        return pixels


def load_textures(ih):
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    # target,level,internalformat,width,height,border,format,type,pixels
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, ih.get_width(), ih.get_height(), 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, ih.get_pixels())

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
    global texts
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
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, imageHelper.get_width(), imageHelper.get_height(), 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, imageHelper.get_pixels())
        display()
    if key == b'r':
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, imageHelper.get_width(), imageHelper.get_height(), 0, GL_RGB, GL_UNSIGNED_BYTE, imageHelper.get_red_image())
        display()
    if key == b'b':
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, imageHelper.get_width(), imageHelper.get_height(), 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, imageHelper.get_image_with_bit_map())
        display()

glutInit(sys.argv)
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)  # Bit mask to select a single buffered window, and RGBA mode window.
loadImage()
glutInitWindowSize(imageHelper.get_width(), imageHelper.get_height())
glutInitWindowPosition(200, 200)
glutCreateWindow('Practice 1')
init()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutMainLoop()
