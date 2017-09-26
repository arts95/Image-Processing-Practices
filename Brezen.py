import sys
import math

try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except:
    print
    '''
   ERROR: PyOpenGL not installed properly.
           '''
    sys.exit()

global pointsToConvert

def drawPoint(dot1):
    glBegin(GL_POINTS)
    glVertex3f(dot1[0], dot1[1], 0.0)
    glEnd()


def convertCartesianToCylindrical(dots):
    cylindricalDots = []
    for dot in dots:
        r = math.sqrt(dot[0] * dot[0] + dot[1] * dot[1])
        o = math.atan(dot[1] / dot[0])
        cylindricalDots.append([r, o, dot[2]])
    return cylindricalDots


def Bresenham8Line(x0, y0, x1, y1):
    # change of coordinates
    dx = (x1 - x0) if (x1 > x0) else (x0 - x1)
    dy = (y1 - y0) if (y1 > y0) else (y0 - y1)

    # Direction of increments
    sx = 1 if (x1 >= x0) else (-1)
    sy = 1 if (y1 >= y0) else (-1)

    dots = [[x0, y0, 0.0]]
    if dy < dx:
        d1 = dy * 2
        d = d1 - dx
        d2 = (dy - dx) * 2
        x = x0 + sx
        y = y0
        for i in range(1, int(dx)):
            if d > 0:
                d += d2
                y += sy
            else:
                d += d1
            dots.append([x, y, 0.0])
            x += sx
    else:
        d1 = dx * 2
        d = d1 - dy
        d2 = (dx - dy) * 2
        x = x0
        y = y0 + sy
        for i in range(1, int(dy)):
            if d > 0:
                d += d2
                x += sx
            else:
                d += d1
            dots.append([x, y, 0.0])
            y += sy
    return dots


def Bresenham4Line(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    d = 0
    d1 = dy * 2
    d2 = -(dx * 2)
    dots = [[x0, y0, 0.0]]
    x = x0
    y = y0

    for i in range(1, int(dx + dy)):
        if d > 0:
            d += d2
            y = y + 1
        else:
            d += d1
            x = x + 1
        dots.append([x, y, 0.0])

    return dots


def init():
    # clear screen red, green, blue, alpha
    glClearColor(1.0, 1.0, 1.0, 0.0)
    # select flat or smooth shading
    glShadeModel(GL_FLAT)


def display():
    # clear buffers to preset values
    glClear(GL_COLOR_BUFFER_BIT)  # Indicates the buffers currently enabled for color writing.
    # set color
    glColor3f(0.0, 0.0, 0.0)
    # get dots for line
    global pointsToConvert
    pointsToConvert = Bresenham4Line(100.0, 100.0, 300.0, 300.0)

    # draw line
    for dot in pointsToConvert:
        drawPoint(dot)

    # force execution of GL commands in finite time
    glFlush()


def reshape(w, h):
    glViewport(0, 0, w, h)
    # specify which matrix is the current matrix
    glMatrixMode(GL_PROJECTION)  # Applies subsequent matrix operations to the projection matrix stack.
    glLoadIdentity()
    gluOrtho2D(0.0, w, 0.0, h)


def keyboard(key, x, y):
    if key == chr(99).encode():
        print(pointsToConvert)
        print(convertCartesianToCylindrical(pointsToConvert))

    if key == chr(27).encode():
        sys.exit(0)


# initialize the GLUT library.
glutInit(sys.argv)
# sets the initial display mode.
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)  # Bit mask to select a single buffered window, an RGBA mode window.
glutInitWindowSize(400, 400)
glutInitWindowPosition(100, 100)
glutCreateWindow('Line')
init()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutMainLoop()
