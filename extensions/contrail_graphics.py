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

import numpy

import pymorphous.simulator_graphics

from PySide2 import QtCore, QtWidgets, QtOpenGL

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


class Window(QtWidgets.QWidget):
    def __init__(self, cloud, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.glWidget = ContrailGLWidget(cloud)
        
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        
        self.setWindowTitle(self.tr(cloud.window_title))
        
class ContrailGLWidget(pymorphous.simulator_graphics._SimulatorGLWidget):
    
    def __init__(self, cloud, parent=None):
        pymorphous.simulator_graphics._SimulatorGLWidget.__init__(self, cloud, parent)
        
        self.trail = {}
        for d in cloud.devices:
            self.trail[d] = []
    
    def __del__(self):
        self.makeCurrent()
        glDeleteLists(self.listSimpleBody, 1)
        
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)   
        glutInit()
        
        self.listTrailBody = glGenLists(1);
        if not self.listTrailBody:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listTrailBody, GL_COMPILE)
        glutSolidSphere(0.4, 8, 8)
        glEndList()

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
    
    def set3dRotation(self):
        glLoadIdentity()
        glClearColor(0,0,0,1) 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
        glViewport(0,0,self.width(),self.height())

        glMatrixMode(GL_PROJECTION)
        
        gluPerspective(45.0,float(self.width())/self.height(),0.1,200.0)    #setup lens
        glTranslatef(0, 0, -150.0)                #move back
        #glRotatef(60, 1, 60, 90)                       #orbit higher
        
    def paintGL(self):
        self.set3dRotation()
        
        glPushMatrix()
        glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        for d in self.cloud.devices:
            for p in self.trail[d]:
                glPushMatrix()
                glTranslatef(p[0],p[1],p[2])
                glColor4f(1,1,1,1)
                glCallList(self.listTrailBody)
                glPopMatrix()
            self.trail[d] += [numpy.array(d.coord)]
        glPopMatrix()
        if self.recording:
            self.save_image(image=False)
        self.frameno += 1
    
    def resizeGL(self, width, height):
        self.set3dRotation()
            
def contrail_graphics(cloud):
    app = QtWidgets.QApplication(sys.argv)
    window = Window(cloud = cloud)
    window.show()
    sys.exit(app.exec_())
