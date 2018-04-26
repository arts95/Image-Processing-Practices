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


class ImageFilter:
    @classmethod
    def get_first_mask(cls):
        return [[1 / 9, 1 / 9, 1 / 9], [1 / 9, 1 / 9, 1 / 9], [1 / 9, 1 / 9, 1 / 9]]

    @classmethod
    def get_second_mask(cls):
        return [[0, 1 / 6, 0], [1 / 6, 2 / 6, 1 / 6], [0, 1 / 6, 0]]

    @classmethod
    def get_third_mask(cls):
        return [[1 / 16, 2 / 16, 1 / 16], [2 / 16, 4 / 16, 2 / 16], [1 / 16, 2 / 16, 1 / 16]]

    @classmethod
    def get_result(cls, mask, matrix):
        mask = np.array(mask).ravel()
        matrix = np.array(matrix).ravel()
        result = 0
        for i, mask_value in enumerate(mask):
            for j, matrix_value in enumerate(matrix):
                if i == j:
                    result += mask_value * matrix_value

        return result

    @classmethod
    def get_masks(cls):
        return {
            1: cls.get_first_mask(),
            2: cls.get_second_mask(),
            3: cls.get_third_mask(),
        }

    @classmethod
    def get_mask(cls, mask):
        if mask in cls.get_masks():
            return cls.get_masks()[mask]
        else:
            return cls.get_first_mask()


class ImageHelper:
    def __init__(self, image):
        self.image = image
        self.loaded_pixel = self.get_pixels()

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

    def get_filtered_image(self, mask):
        pixels = []
        mask = ImageFilter.get_mask(mask)
        for i, row in enumerate(self.get_pixels()):
            new_row = []
            for j, value in enumerate(row):
                try:
                    filtered_value = ImageFilter.get_result(mask, self.get_matrix_of_neighbors(i, j))
                    new_row.append(int(filtered_value))
                except IndexError:
                    new_row.append(value)
            pixels.append(new_row)
        return pixels

    def find_min_max(self):
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
        max = self.find_min_max()['max']
        min_peak = coefficient_min * max
        max_peak = coefficient_max * max
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


def load_textures(ih):
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    gl_tex_image_2d()
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


def load_image():
    global imageHelper
    Tk().withdraw()
    filename = askopenfilename()
    image = dicom.read_file(filename)
    if filename == '':
        sys.exit()
    imageHelper = ImageHelper(image)
    if imageHelper.get_bits_allocated() != 16:
        sys.exit()

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
    if key == b'1' or key == b'2' or key == b'3':
        imageHelper.set_loaded_pixel(imageHelper.get_filtered_image(int(key)))
        gl_tex_image_2d()
        display()
        draw_text("Filter #" + str(int(key)), 100, imageHelper.get_height() - 20)
        glFlush()


def move(x, y):
    text = "brightness: " + str("{0:.2f}".format(imageHelper.get_brightness_of_pixel(x, y)))
    display()
    draw_text(text, 90, imageHelper.get_height() - 20)
    glFlush()


def draw_text(text, x, y):
    glDisable(GL_TEXTURE_2D)
    glColor3f(255, 255, 255)
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(character))
    glEnable(GL_TEXTURE_2D)


# def motion(x1, y1):
#     move(x1, y1)
#     glFlush()


glutInit(sys.argv)
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)  # Bit mask to select a single buffered window, and RGBA mode window.
load_image()
glutInitWindowSize(imageHelper.get_width(), imageHelper.get_height())
glutInitWindowPosition(200, 200)
glutCreateWindow('Practice 3')
init()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
# glutPassiveMotionFunc(motion)
glutMainLoop()
