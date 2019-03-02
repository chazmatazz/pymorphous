# Copyright (C) 2011 by Charles Dietrich
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time
from PySide2 import QtCore, QtWidgets, QtOpenGL
import sys
import math

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
except ImportError:
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None, "PyMorphous",
                            "PyOpenGL must be installed to run PyMorphous.",
                            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Default,
                            QtWidgets.QMessageBox.NoButton)
    sys.exit(1)
    
from PIL import Image

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

class _SimulatorWindow(QtWidgets.QWidget):
    def __init__(self, cloud, widget, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.cloud = cloud
        self.glWidget = widget(cloud)
        mainLayout = QtWidgets.QVBoxLayout()
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
        
    def resizeGL(self, width, height):
        glViewport(0, 0, self.width(), self.height())
        self.set3dProjection()
