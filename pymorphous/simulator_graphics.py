"""
Provides the simulator graphics implementation
public:
simulator_graphics
"""

import time
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

import pymorphous.simulator_constants

class _SimulatorWindow(QtGui.QWidget):
    def __init__(self, cloud, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.glWidget = _SimulatorGLWidget(cloud)
        
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        
        self.setWindowTitle(self.tr(cloud.window_title))

# the color code of the ground is 0
_color_id_counter = 1

def _get_color_id(lst):
    return lst[0] + lst[1]*255 + lst[2]*255*255

class _SimulatorUniqueColor(object):
    def __init__(self):
        global _color_id_counter
        self.value = _color_id_counter
        _color_id_counter += 1
        
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
        
class _SimulatorGLWidget(QtOpenGL.QGLWidget):
    
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
        glDeleteLists(self.listSimpleBody, 1)
        glDeleteLists(self.listSelect, 1)
        glDeleteLists(self.listRadio, 1)
        glDeleteLists(self.listSelectIndicator, 1)
        for i in range(3):
            glDeleteLists(self.listLeds[i], 1)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(*self.cloud.settings.graphics.background)    
        glutInit()
        
        self.listSimpleBody = glGenLists(1);
        if not self.listSimpleBody:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listSimpleBody, GL_COMPILE)
        glutWireSphere(0.8, 2, 2)
        glEndList()
        
        self.listSelect = glGenLists(1);
        if not self.listSelect:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listSelect, GL_COMPILE)
        glutSolidSphere(0.8*4, 8, 8)
        glEndList()

        self.listSelectIndicator = glGenLists(1);
        if not self.listSelectIndicator:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listSelectIndicator, GL_COMPILE)
        glutSolidSphere(0.8*4, 8, 8)
        glEndList()
        
        self.listRadio = glGenLists(1);
        if not self.listRadio:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listRadio, GL_COMPILE)
        glutSolidSphere(0.8*4, 8, 8)
        glEndList()
        
        self.listSenses = []
        for i in range(3):
            self.listSenses += [glGenLists(1)]
            if not self.listSenses[i]:
                raise SystemError("""Unable to generate display list using glGenLists""")
            glNewList(self.listSenses[i], GL_COMPILE)
            glutSolidSphere(0.4, 8, 8)
            glEndList()
            
        self.listLeds = []
        for i in range(3):
            self.listLeds += [glGenLists(1)]
            if not self.listLeds[i]:
                raise SystemError("""Unable to generate display list using glGenLists""")
            glNewList(self.listLeds[i], GL_COMPILE)
            glutSolidSphere(0.4, 8, 8)
            glEndList()
        
        self.color_dict = {}
        for d in self.cloud.devices:
            d.color_id = _SimulatorUniqueColor()
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
        r = (pixel[0][0].tolist())
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
            self.cloud.show_leds = not self.cloud.show_leds
            self.updateGL()
            
        dirs = {QtCore.Qt.Key_Left: [-1,0],
                QtCore.Qt.Key_Right: [1,0],
                QtCore.Qt.Key_Up: [0,1],
                QtCore.Qt.Key_Down: [0,-1]}
        for (k,v) in dirs.items():
            if key == k:
                glTranslatef(10*v[0], 10*v[1], 0)
                self.updateGL()
                
        if key == QtCore.Qt.Key_3:
            self.cloud.led_stacking_mode = (self.cloud.led_stacking_mode+1)%3
            self.updateGL()
            
        if key == QtCore.Qt.Key_B:
            self.cloud.show_body = not self.cloud.show_body
            self.updateGL()
            
    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(self.cloud.window_width, self.cloud.window_height)
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
        
        self.mypaint(True)
        
    def mypaint(self, real):
        glPushMatrix()
        glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        for d in self.cloud.devices:
            x = d.x
            y = d.y
            z = d.z
            glPushMatrix()
            glTranslatef(x,y,z)
            if real:
                if self.cloud.show_body:
                    glColor4f(*self.cloud.settings.graphics.simple_body)
                    glCallList(self.listSimpleBody)
                    for i in range(3):
                        if d.senses[i] != 0:
                            glColor4f(*self.cloud.settings.graphics._user_sensors[i])
                            glCallList(self.listSenses[i])
                    if d == self.selected_device:
                        glColor4f(*self.cloud.settings.graphics.selected_device)
                        glCallList(self.listSelectIndicator)
                        
                if self.cloud.show_radio:
                    glColor4f(*self.cloud.settings.graphics.radio_range_ring)
                    glCallList(self.listRadio)
                
                if self.cloud.show_leds:
                    
                    leds = [0,0,0]
                    if not self.cloud.led_flat:
                        if self.cloud.led_stacking_mode == pymorphous.simulator_constants.LED_STACKING_MODE_DIRECT:
                            acc = 0
                            for i in range(3):
                                leds[i] = d.leds[i]+acc
                                acc += d.leds[i]
                        elif self.cloud.led_stacking_mode == pymorphous.simulator_constants.LED_STACKING_MODE_OFFSET:
                            for i in range(3):
                                leds[i] = d.leds[i]+i
                        else:
                            for i in range(3):
                                leds[i] = d.leds[i]
                        
                    for i in range(3):
                        if d.leds[i] != 0:
                            glPushMatrix()
                            glTranslatef(0,0,leds[i])
                            glColor4f(*self.cloud.settings.graphics._leds[i])
                            glCallList(self.listLeds[i])
                            glPopMatrix()
            else:
                if self.cloud.show_body:
                    glColor3f(d.color_id.redf, d.color_id.greenf, d.color_id.bluef)
                    glCallList(self.listSelect)
            glPopMatrix()
        glPopMatrix()
    
    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glLoadIdentity();
        
        glMatrixMode(GL_PROJECTION)
        
        gluPerspective(45.0,float(width)/height,0.1,200.0)    #setup lens
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
            
def simulator_graphics(cloud):
    app = QtGui.QApplication(sys.argv)
    window = _SimulatorWindow(cloud = cloud)
    window.show()
    sys.exit(app.exec_())
