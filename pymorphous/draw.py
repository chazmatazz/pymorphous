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

# the color code of the ground is 0
color_id_counter = 1

def get_color_id(lst):
    return lst[0] + lst[1]*255 + lst[2]*255*255

class UniqueColor(object):
    def __init__(self):
        global color_id_counter
        self.value = color_id_counter
        color_id_counter += 1
        
    @property
    def red(self):
        return self.value % 255
    
    @property
    def green(self):
        return (self.value/255) % 255
    
    @property
    def blue(self):
        return self.value/(255*255) % 255
    
    @property
    def redf(self):
        return self.red / 255.0
    
    @property
    def greenf(self):
        return self.green / 255.0
    
    @property
    def bluef(self):
        return self.blue / 255.0
        
class GLWidget(QtOpenGL.QGLWidget):
    
    def __init__(self, cloud, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        
        self.cloud = cloud
        
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.selected_device = None
        
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.myupdate)
        timer.start(1000.0/self.cloud.desired_fps)
        self.last_time = time.time()
    
    def __del__(self):
        self.makeCurrent()
        glDeleteLists(self.deviceList, 1)
        glDeleteLists(self.selectList, 1)
        glDeleteLists(self.selectIndicatorList, 1)
        for i in range(3):
            glDeleteLists(self.ledLists[i], 1)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)    
        glutInit()
        
        
        self.bodyList = glGenLists(1);
        if not self.bodyList:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.bodyList, GL_COMPILE)
        glutSolidSphere(0.8, 8, 8)
        glEndList()
        
        self.selectList = glGenLists(1);
        if not self.selectList:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.selectList, GL_COMPILE)
        glutSolidSphere(0.8*4, 8, 8)
        glEndList()

        self.selectIndicatorList = glGenLists(1);
        if not self.selectIndicatorList:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.selectIndicatorList, GL_COMPILE)
        glutWireSphere(0.8*4, 8, 8)
        glEndList()
        
        self.ledLists = []
        for i in range(3):
            self.ledLists += [glGenLists(1)]
            if not self.ledLists[i]:
                raise SystemError("""Unable to generate display list using glGenLists""")
            glNewList(self.ledLists[i], GL_COMPILE)
            glutSolidSphere(0.4, 8, 8)
            glEndList()
        
        self.color_dict = {}
        for d in self.cloud.devices:
            d.color_id = UniqueColor()
            self.color_dict[d.color_id.value] = d
    
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
        self.mypaint(False)
        pixel = glReadPixels(event.pos().x(), event.pos().y(), 1, 1, GL_RGB, GL_BYTE)
        r = get_color_id(pixel[0][0].tolist())
        try:
            d = self.color_dict[r]
            if d == self.selected_device:
                self.selected_device = None
            else:
                self.selected_device = d
        except:
            self.selected_device = None
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
    
    def keyPressEvent(self, event):
        key = event.key()
        
        sense_keys = [QtCore.Qt.Key_T, QtCore.Qt.Key_Y, QtCore.Qt.Key_U]
        for i in range(len(sense_keys)):
            if key == sense_keys[i]:
                if self.selected_device:
                    self.selected_device.senses[i] = not self.selected_device.senses[i]
                    self.updateGL()
                    
        if key == QtCore.Qt.Key_L:
            self.cloud.display_leds = not self.cloud.display_leds
            self.updateGL()
            
        dirs = {QtCore.Qt.Key_Left: [-1,0],
                QtCore.Qt.Key_Right: [1,0],
                QtCore.Qt.Key_Up: [0,1],
                QtCore.Qt.Key_Down: [0,-1]}
        for (k,v) in dirs.items():
            if key == k:
                glTranslatef(10*v[0], 10*v[1], 0)
                self.updateGL()
        
            
    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(self.cloud.width, self.cloud.height)
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
        
        self.mypaint(True)
        
    def mypaint(self, real):
        glPushMatrix()
        glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        for d in self.cloud.devices:
            x = d.x*50
            y = d.y*50
            z = d.z*50
            glPushMatrix()
            glTranslatef(x,y,z)
            if real:
                c = [0,0,0]
                c[0] += (1.0 if d.senses[0] else 0.0)/2
                c[1] += (1.0 if d.senses[0] else 0.0)/2
                c[1] += (1.0 if d.senses[1] else 0.0)/2
                c[2] += (1.0 if d.senses[1] else 0.0)/2
                c[2] += (1.0 if d.senses[2] else 0.0)/2
                c[0] += (1.0 if d.senses[2] else 0.0)/2
                if c == [0,0,0]:
                    c = [1.0,1.0,1.0]
                    
                glColor3f(c[0],c[1],c[2])
                glCallList(self.bodyList)
                if d == self.selected_device:
                    glColor3f(1.0, 1.0, 1.0)
                    glCallList(self.selectIndicatorList)
                if self.cloud.display_leds:
                    for i in range(3):
                        if d.leds[i] != 0:
                            glPushMatrix()
                            glTranslatef(0,0,d.leds[i])
                            glColor3f(1.0 if i==0 else 0.0, 1.0 if i==1 else 0.0, 1.0 if i==2 else 0.0)
                            glCallList(self.ledLists[i])
                            glPopMatrix()
            else:
                glColor3f(d.color_id.redf, d.color_id.greenf, d.color_id.bluef)
                glCallList(self.selectList)
            glPopMatrix()
        glPopMatrix()
    
    def resizeGL(self, width, height):
        side = min(width, height)
        #glViewport((width - side) / 2, (height - side) / 2, side, side)

        glMatrixMode(GL_PROJECTION)
        
        gluPerspective(45.0,float(self.cloud.width)/self.cloud.height,0.1,200.0)    #setup lens
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
            
def display_cloud(cloud):
    app = QtGui.QApplication(sys.argv)
    window = Window(cloud = cloud)
    window.show()
    sys.exit(app.exec_())
