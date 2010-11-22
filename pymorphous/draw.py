import time

from pymorphous import *

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

class Window(QtGui.QWidget):
    def __init__(self, cloud, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.glWidget = GLWidget(cloud)
        
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        
        self.setWindowTitle(self.tr(cloud.window_title))
        
        
class GLWidget(QtOpenGL.QGLWidget):
    xRotationChanged = QtCore.Signal(int)
    yRotationChanged = QtCore.Signal(int)
    zRotationChanged = QtCore.Signal(int)
    
    def __init__(self, cloud, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        
        self.cloud = cloud
        
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.myupdate)
        timer.start(1000.0/self.cloud.desired_fps)
        self.last_time = time.time()
    
    def __del__(self):
        self.makeCurrent()
        glDeleteLists(self.deviceList, 1)
        for i in range(3):
            glDeleteLists(self.ledList[i], 1)
    
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
            self.xRotationChanged.emit(angle)
            self.updateGL()

    @yRotation.setter
    def yRotation(self, angle):
        self.normalizeAngle(angle)

        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.updateGL()

    @zRotation.setter
    def zRotation(self, angle):
        self.normalizeAngle(angle)

        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
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
        return QtCore.QSize(self.cloud.width, self.cloud.height)
    
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)    
        glutInit()   
        self.deviceList = glGenLists(1);
        if not self.deviceList:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.deviceList, GL_COMPILE)
        glutSolidSphere(0.4, 8, 8)
        glEndList()
        self.ledList = []
        for i in range(3):
            self.ledList += [glGenLists(1)]
            if not self.ledList[i]:
                raise SystemError("""Unable to generate display list using glGenLists""")
            glNewList(self.ledList[i], GL_COMPILE)
            glutSolidSphere(0.4, 8, 8)
            glEndList()
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 

        glPushMatrix()
        glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        for d in self.cloud.devices:
            x = d.x*50
            y = d.y*50
            z = d.z*50
            leds = d.leds
            glPushMatrix()
            glTranslatef(x,y,z)
            glColor3f(1.0, 1.0, 1.0)
            glCallList(self.deviceList)
            glPopMatrix()
            
            for i in range(3):
                if leds[i] != 0:
                    glPushMatrix()
                    glTranslatef(x,y,z+leds[i])
                    glColor3f(1.0 if i==0 else 0.0, 1.0 if i==1 else 0.0, 1.0 if i==2 else 0.0)
                    glCallList(self.ledList[i])
                    glPopMatrix()
        glPopMatrix()
    
    def resizeGL(self, width, height):
        side = min(width, height)
        #glViewport((width - side) / 2, (height - side) / 2, side, side)

        glMatrixMode(GL_PROJECTION)
        
        gluPerspective(45.0,float(self.cloud.width)/self.cloud.height,0.1,200.0)    #setup lens
        glTranslatef(0.0, 0.0, -150.0)                #move back
        glRotatef(60, 1, 60, 90)                       #orbit higher
    
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
def display_cloud(cloud):
    app = QtGui.QApplication(sys.argv)
    window = Window(cloud = cloud)
    window.show()
    sys.exit(app.exec_())
