import time
from PySide import QtCore, QtGui, QtOpenGL
import sys
import math

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
    
import Image

import pymorphous.implementation.simulator.constants

def _spherical_to_rect(c):
    """
    http://en.wikipedia.org/wiki/Spherical_coordinate_system
    """
    r = c[0]
    theta = c[1]
    phi = c[2]
    return [r * math.sin(theta) * math.cos(phi), r * math.sin(theta) * math.sin(phi), r * math.cos(theta)]

def _radian_to_deg(rad):
    return rad * 360 / (2 * math.pi)

class _SimulatorWindow(QtGui.QWidget):
    def __init__(self, cloud, widget, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.cloud = cloud
        self.glWidget = widget(cloud)
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        
        self.setWindowTitle(self.tr(cloud.window_title))

_color_id_counter = 0

def _get_color_id(lst):
    return lst[0] + lst[1]*128 + lst[2]*128*128

class _SimulatorUniqueColor(object):
    def __init__(self):
        global _color_id_counter
        self.value = _color_id_counter
        _color_id_counter += 1
        
    @property
    def red(self):
        return self.value % 128
    
    @property
    def green(self):
        return (self.value/128) % 128
    
    @property
    def blue(self):
        return self.value/(128*128) % 128

class _BaseSimulatorWidget(QtOpenGL.QGLWidget):
    
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
        self.start_time = time.time()
        self.recording = self.cloud.auto_record
        self.frameno = 0
        
        self.color_dict = {}
        for d in self.cloud.devices:
            d.color_id = _SimulatorUniqueColor()
            self.color_dict[str(d.color_id.value)] = d
    
    def __del__(self):
        self.makeCurrent()
        
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glutInit()
    
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
            
    def save_image(self, image=True):
        if image:
            basedir = self.cloud.settings.runtime.dir_image
        else:
            basedir = self.cloud.settings.runtime.tmp_dir_video
        
        width, height = self.width(), self.height()
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixelsub(0, 0, width, height, GL_RGB)
        assert data.shape == (width,height,3), """Got back array of shape %r, expected %r"""%(
            data.shape,
            (width,height,3),
        )
        image = Image.fromstring( "RGB", (width, height), data.tostring())
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        dir = os.path.join(basedir, "%s" % self.start_time)
        if not os.path.isdir(dir):
            os.makedirs(dir)
        filename = os.path.join(dir, "%s.png" % self.frameno)
        image.save(filename, "PNG")

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(self.cloud.window_width, self.cloud.window_height)
    
    def paintGL(self):
        self.mypaint(True)

    def set3dProjection(self, real=True):
        glLoadIdentity();
        glViewport(0, 0, self.width(), self.height())
        if real:
            glClearColor(*self.cloud.settings.graphics.background_color)
            glEnable(GL_TEXTURE_2D)
        else:
            glClearColor(1,1,1,1)
            glDisable(GL_LIGHTING)
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            glShadeModel(GL_FLAT)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
        glMatrixMode(GL_PROJECTION)
        
    def resizeGL(self, width, height):
        self.set3dProjection()
    
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
            
    def select_device(self, event):
        self.mypaint(False)
        pixel = glReadPixels(event.pos().x(), self.height()-event.pos().y(), 1, 1, GL_RGB, GL_BYTE)
        r = str((_get_color_id(pixel[0][0].tolist())))
        try:
            return self.color_dict[r]
        except KeyError:
            return None

def _simulator_graphics(cloud, widget):
    app = QtGui.QApplication(sys.argv)
    window = _SimulatorWindow(cloud = cloud, widget=widget)
    window.show()
    sys.exit(app.exec_())
