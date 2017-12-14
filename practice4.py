from tkinter import Tk
from tkinter.filedialog import askopenfilename
import sys
import dicom
import uuid
from dicom.tag import Tag

try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *

except:
    print(''' ERROR: PyOpenGL not installed properly. ''')
    sys.exit()


class Text():
    def __init__(self, label, value):
        self.label = label
        self.value = value

    def __str__(self):
        return str(self.label) + ": " + str(self.value) + ";"


def LoadTextures(pixels):
    # Create Texture
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1))
    # target,level,internalformat,width,height,border,format,type,pixels
    glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, width, height, 0, GL_LUMINANCE, GL_FLOAT, getPixelsForDrawing(pixels))
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


def loadImage():
    global width, height, image
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    if filename == '':
        sys.exit()
    image = dicom.read_file(filename)
    width = image['0028', '0011'].value
    height = image['0028', '0010'].value
    return image


def getPixelsForDrawing(pixels):
    data = []
    max = findMinMax(pixels)[1]
    for row in pixels:
        newRow = []
        for pixel in row:
            newRow.append(pixel / max)
        data.append(newRow)
    return data


def prepareData(m, b):
    pixels = []
    for row in image.pixel_array:
        newRow = []
        for pixel in row:
            if pixel > 175:
                value = m * 175 + b
            elif pixel < 10:
                value = m * 10 - b
            else:
                value = m * pixel + b
            newRow.append(float(value))
        pixels.append(newRow)
    return pixels


def saveImage(m, b, minMax):
    image['0008', '0008'].value[0] = 'DERIVED'  # Image Type
    image['0008', '0008'].value[1] = 'SECONDARY'  # Image Type
    image['0008', '103E'].value = 'Description'  # Series description
    image.add_new(Tag(['0008', '103F']), 'LO', 'Series description code')  # Series description
    image.add_new(Tag(['0020', '0016']), 'LO', uuid.uuid4().hex)  # Sop Instance
    image.add_new(Tag(['0002', '0003']), 'LO', image['0020', '0016'].value)  # Sop Instance
    image['0020', '000E'].value = uuid.uuid4().hex  # Series instance UID
    image.add_new(Tag(['0028', '0106']), 'FL', minMax[0])  # Smallest Image Pixel Value
    image.add_new(Tag(['0028', '0107']), 'FL', minMax[1])  # Largest Image Pixel Value
    image['0028', '1052'].value = b  # Rescale intercept
    image['0028', '1053'].value = m  # Rescale slope
    image['0028', '0100'].value = 16  # Rescale slope
    image.save_as("newfilename.dcm")


def findMinMax(data):
    arrayData = []
    for row in data:
        for pixel in row:
            arrayData.append(pixel)

    return [
        min(arrayData),
        max(arrayData)
    ]


def init():
    global texts
    m = 0.0120557
    b = 4.180
    pixels = prepareData(m, b)
    LoadTextures(pixels)
    minMax = findMinMax(pixels)
    saveImage(m, b, minMax)
    texts = [Text('Smallest Image Pixel Value', minMax[0]), Text('Largest Image Pixel Value', minMax[1]),
             Text('Rescale intercept', b), Text('Rescale slope', m), Text('Value representation', 'FLOAT')]
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
    if key == b'\r':
        addPixel = 0
        for text in texts:
            draw_text(str(text), 10, height + 80 - addPixel)
            addPixel += 15
        glFlush()


def draw_text(text, x, y):
    glDisable(GL_TEXTURE_2D)
    glColor3f(255, 255, 255)
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(character))
    glEnable(GL_TEXTURE_2D)

# initialize the GLUT library.
glutInit(sys.argv)
# sets the initial display mode.
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)  # Bit mask to select a single buffered window, and RGBA mode window.
loadImage()
glutInitWindowSize(width, height + 100)
glutInitWindowPosition(100, 100)
glutCreateWindow('Practice 4')
init()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutMainLoop()
