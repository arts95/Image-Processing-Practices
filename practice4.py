# from tkinter import Tk
# from tkinter.filedialog import askopenfilename
import dicom
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
global width, height


def LoadTextures():
    global width, height

    # Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    # filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    # ds = dicom.read_file(filename)
    # ds = dicom.read_file("DICOM_Image_for_Lab_2.dcm")
    # m = 0.0120557
    # b = 4.180

    # data = []

    # for row in ds.pixel_array:
    #     newRow = []
    #     for pixel in row:
    #         newRow.append((m * pixel + b))
    #     data.append(newRow)

    image = dicom.read_file("DICOM_Image_for_Lab_2.dcm")
    width = image['0028', '0011'].value
    height = image['0028', '0010'].value
    pixelsData = image.PixelData

    image = np.fromstring(pixelsData, np.byte)

    # Create Texture
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))  # 2d texture (x and y size)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, width, height, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, image)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


def init():
    LoadTextures()
    # clear screen red, green, blue, alpha
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)  # This Will Clear The Background Color To Black

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()  # Reset The Projection Matrix
    glMatrixMode(GL_MODELVIEW)


def display():
    global width, height

    glClearColor(0.0, 0.0, 0.0, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_QUADS)

    glTexCoord2f(0.0, 0.0)
    glVertex2f(0.0, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0.0, width)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(height, width)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(height, 0.0)

    glEnd()
    glFlush()


def reshape(w, h):
    glViewport(0, 0, w, h)
    # specify which matrix is the current matrix
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluOrtho2D(0.0, w, 0.0, h)


def keyboard(key, x, y):
    if key == chr(27).encode():
        sys.exit(0)


# initialize the GLUT library.
glutInit(sys.argv)
# sets the initial display mode.
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)  # Bit mask to select a single buffered window, and RGBA mode window.
glutInitWindowSize(270, 270)
glutInitWindowPosition(100, 100)
glutCreateWindow('Line')
init()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutMainLoop()
