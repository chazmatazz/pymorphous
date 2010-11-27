import time

import numpy

import pymorphous

from PySide import QtCore, QtGui, QtOpenGL

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "PyMorphous",
                            "PyOpenGL must be installed to run PyMorphous.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)

class _DrawDefaults(object):
    def __init__(self):
        self.BACKGROUND = (0, 0, 0, 0)
        self.SIMPLE_BODY = (1, 0.25, 0, 0.8)
        self.TRAIL_BODY = (1, 1, 1, 0.8)

DRAW_DEFAULTS = _DrawDefaults()

class Window(QtGui.QWidget):
    def __init__(self, cloud, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.glWidget = GLWidget(cloud)
        
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        
        self.setWindowTitle(self.tr(cloud.window_title))
        
class GLWidget(QtOpenGL.QGLWidget):
    
    def __init__(self, cloud, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        
        self.cloud = cloud
        
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        self.trail = {}
        for d in self.cloud.devices:
            self.trail[d] = []
        
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.myupdate)
        timer.start(1000.0/self.cloud.desired_fps)
        self.last_time = time.time()
    
    def __del__(self):
        self.makeCurrent()
        glDeleteLists(self.listSimpleBody, 1)
        
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(*DRAW_DEFAULTS.BACKGROUND)    
        glutInit()
        
        self.listTrailBody = glGenLists(1);
        if not self.listTrailBody:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listTrailBody, GL_COMPILE)
        glutSolidSphere(0.4, 8, 8)
        glEndList()
        
        self.listSimpleBody = glGenLists(1);
        if not self.listSimpleBody:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listSimpleBody, GL_COMPILE)
        glutWireSphere(0.8, 2, 2)
        glEndList()
    
    @property
    def xRotation(self):
        return self.xRot

    @property
    def yRotation(self):
        return self.yRot

    @property
    def zRotation(self):
        return self.zRot
    
    @xRotation.setter
    def xRotation(self, angle):
        self.normalizeAngle(angle)

        if angle != self.xRot:
            self.xRot = angle
            self.updateGL()

    @yRotation.setter
    def yRotation(self, angle):
        self.normalizeAngle(angle)

        if angle != self.yRot:
            self.yRot = angle
            self.updateGL()

    @zRotation.setter
    def zRotation(self, angle):
        self.normalizeAngle(angle)

        if angle != self.zRot:
            self.zRot = angle
            self.updateGL()

    def mousePressEvent(self, event):
        self.lastPos = event.pos()
        
    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & QtCore.Qt.LeftButton:
            self.xRotation = self.xRot + 8 * dy
            self.yRotation = self.yRot + 8 * dx
        elif event.buttons() & QtCore.Qt.RightButton:
            self.xRotation = self.xRot + 8 * dy
            self.zRotation = self.zRot + 8 * dx

        self.lastPos = event.pos()
            
    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(self.cloud.window_width, self.cloud.window_height)
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
        
        glPushMatrix()
        glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        for d in self.cloud.devices:
            for p in self.trail[d]:
                glPushMatrix()
                glTranslatef(p[0],p[1],p[2])
                glColor4f(*DRAW_DEFAULTS.TRAIL_BODY)
                glCallList(self.listTrailBody)
                glPopMatrix()
            glPushMatrix()
            glTranslatef(d.x,d.y,d.z)
            self.trail[d] += [numpy.array(d.coord)]
            glColor4f(*DRAW_DEFAULTS.SIMPLE_BODY)
            glCallList(self.listSimpleBody)
            glPopMatrix()
        glPopMatrix()
    
    def resizeGL(self, width, height):
        side = min(width, height)
        #glViewport((width - side) / 2, (height - side) / 2, side, side)

        glMatrixMode(GL_PROJECTION)
        
        gluPerspective(45.0,float(self.cloud.window_width)/self.cloud.window_height,0.1,200.0)    #setup lens
        glTranslatef(0, 0, -150.0)                #move back
        #glRotatef(60, 1, 60, 90)                       #orbit higher
    
    def myupdate(self):
        now = time.time()
        delta = now - self.last_time
        self.cloud.update(delta)
        self.last_time = now
        self.updateGL()
    
    def normalizeAngle(self, angle):
        while (angle < 0):
            angle += 360 * 16

        while (angle > 360 * 16):
            angle -= 360 * 16
            
def contrail_graphics(cloud):
    app = QtGui.QApplication(sys.argv)
    window = Window(cloud = cloud)
    window.show()
    sys.exit(app.exec_())
