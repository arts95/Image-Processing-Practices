from tkinter import Tk
from tkinter.filedialog import askopenfilename
import sys
import dicom
import numpy as np

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
        max_min = self.get_min_max()
        self.max = max_min['max']
        self.min = max_min['min']

    def get_bits_allocated(self):
        return self.image['0028', '0100'].value

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

    def get_matrix_of_neighbors(self, i, j):
        ps = self.get_pixels()
        return [[ps[i - 1][j - 1], ps[i][j - 1], ps[i + 1][j - 1]],
                [ps[i - 1][j], ps[i][j], ps[i + 1][j]],
                [ps[i - 1][j + 1], ps[i][j + 1], ps[i + 1][j + 1]]]

    def get_min_max(self):
        array_data = []
        for row in self.get_pixels():
            for pixel in row:
                array_data.append(pixel)

        return {
            'min': min(array_data),
            'max': max(array_data)
        }

    def get_normalize(self):
        coefficient_min = 0.25
        coefficient_max = 0.85
        min_peak = coefficient_min * self.max
        max_peak = coefficient_max * self.max
        new_min = 0
        new_max = np.iinfo(np.int8).max
        data = []
        for row in self.get_loaded_pixel():
            row_data = []
            for pixel in row:
                new_pixel = int(new_min + (new_max - new_min) * ((pixel - min_peak) / (max_peak - min_peak)))
                if new_pixel < 0:
                    new_pixel = 0
                row_data.append(new_pixel)
            data.append(row_data)

        return data

    def histogram(self):
        hist = [0] * (self.max + 1)
        for row in self.get_pixels():
            for pixel in row:
                hist[pixel] = hist[pixel] + 1
        return hist

    def get_otsu_threshold(self):
        hist = self.histogram()
        sum_all = 0
        for t in range(self.max):
            sum_all += t * hist[t]
        sum_back, w_back, var_max, threshold = 0, 0, 0, 0
        total = self.get_height() * self.get_width()

        for t in range(self.max):
            w_back += hist[t]
            if 0 == w_back: continue
            w_front = total - w_back
            if 0 == w_front: break
            sum_back += t * hist[t]
            mean_back = sum_back / w_back
            mean_front = (sum_all - sum_back) / w_front
            var_between = w_back * w_front * (mean_back - mean_front) ** 2

            if var_between > var_max:
                var_max = var_between
                threshold = t

        return threshold

    def get_otsu_map(self):
        o_map = []
        final_thresh = self.get_otsu_threshold()
        for row in self.get_pixels():
            row_data = []
            for pixel in row:
                if pixel > final_thresh:
                    data = 1
                else:
                    data = 0
                row_data.append(data)
            o_map.append(row_data)

        return o_map

    def get_otsu_pixels(self):
        pixels = []
        o_map = self.get_otsu_map()
        for i, row in enumerate(self.get_pixels()):
            row_data = []
            for j, pixel in enumerate(row):
                row_data.append(np.iinfo(np.int16).max if o_map[i][j] else 0)
            pixels.append(row_data)

        return pixels


def load_textures(ih):
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    gl_tex_image_2d()
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


def load_image():
    global imageHelper
    Tk().withdraw()
    filename = askopenfilename()
    if filename == '':
        sys.exit()
    image = dicom.read_file(filename)
    imageHelper = ImageHelper(image)
    if imageHelper.get_bits_allocated() != 16:
        sys.exit()

    return imageHelper


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


def init():
    load_textures(imageHelper)
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)  # This Will Clear The Background Color To Black
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()  # Reset The Projection Matrix
    glMatrixMode(GL_MODELVIEW)


def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluOrtho2D(0.0, w, 0.0, h)


def gl_tex_image_2d():
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, imageHelper.get_width(), imageHelper.get_height(), 0, GL_LUMINANCE,
                 GL_UNSIGNED_BYTE, imageHelper.get_normalize())


def keyboard(key, x, y):
    if key == chr(27).encode():
        sys.exit(0)
    if key == b'd':
        imageHelper.set_loaded_pixel(imageHelper.get_pixels())
        gl_tex_image_2d()
        display()
    if key == b'o':
        imageHelper.set_loaded_pixel(imageHelper.get_otsu_pixels())
        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, imageHelper.get_width(), imageHelper.get_height(), 0, GL_LUMINANCE,
                     GL_UNSIGNED_BYTE, imageHelper.get_loaded_pixel())
        display()


def draw_text(text, x, y):
    glDisable(GL_TEXTURE_2D)
    glColor3f(255, 255, 255)
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(character))
    glEnable(GL_TEXTURE_2D)


glutInit(sys.argv)
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)  # Bit mask to select a single buffered window, and RGBA mode window.
load_image()
glutInitWindowSize(imageHelper.get_width(), imageHelper.get_height())
glutInitWindowPosition(200, 200)
glutCreateWindow('Practice 4')
init()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutMainLoop()
