import time
from PySide import QtCore, QtGui, QtOpenGL
import sys
import math
import numpy

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

from pymorphous.implementation.simulator.graphics import core

class _WallGLWidget(core._BaseSimulatorWidget):
    def __init__(self, cloud, parent=None):
        core._BaseSimulatorWidget.__init__(self, cloud, parent)
    
    def __del__(self):
        core._BaseSimulatorWidget.__del__(self)

        glDeleteLists(self.listHexBody, 1)

    def initializeGL(self):
        core._BaseSimulatorWidget.initializeGL(self)
        
        if self.cloud.settings.graphics.background:
            img = Image.open(self.cloud.settings.graphics.background) # .jpg, .bmp, etc. also work
            img_data = numpy.array(list(img.getdata()), numpy.int8)
            self.background_image_size = img.size
            background_texture = glGenTextures(1)
            glPixelStorei(GL_UNPACK_ALIGNMENT,1)
            glBindTexture(GL_TEXTURE_2D, background_texture)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.background_image_size[0], self.background_image_size[1], 
                         0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
            
            self.listBackground = glGenLists(1)
            if not self.listBackground:
                raise SystemError("""Unable to generate display list using glGenLists""")
            glNewList(self.listBackground, GL_COMPILE)
            glBegin(GL_QUADS)
            w = self.background_image_size[1]
            h = self.background_image_size[0]
            for v in [(0,0), (w,0), (w,h), (0,h)]:
                glTexCoord2d(*v)
                glVertex2d(*v)
            glEnd()
            glEndList()
            
        self.listHexBody = glGenLists(1)
        if not self.listHexBody:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listHexBody, GL_COMPILE)
        glBegin(GL_POLYGON)
        r = self.cloud.wall_hex_radius
        for i in range(6):
            glVertex2d(r*math.cos(i/6.0*2*math.pi),r*math.sin(i/6.0*2*math.pi))
        glEnd()
        glEndList()
    
    def tabletEvent(self, event):
        for d in self.cloud.devices:
            d._reset_senses()
        if(event.pressure() > 0):
            selected_device = self.select_device(event)
            if selected_device:
                selected_device.sense0 = event.pressure()
    
    def keyPressEvent(self, event):
        key = event.key()
        
        if key == QtCore.Qt.Key_I:
            self.save_image()
        if key == QtCore.Qt.Key_R:
            self.recording = True
        if key == QtCore.Qt.Key_S:
            self.recording = False
        
        
    def mypaint(self, real):
        self.set3dProjection(real)
        
        if real:
            glPushMatrix()
            glTranslatef(-self.background_image_size[0]/2,-self.background_image_size[1]/2,-30)
            glColor3f(1,1,1)
            glCallList(self.listBackground)
            glPopMatrix()
            
        for d in self.cloud.devices:
            x = d.x
            y = d.y
            z = d.z
            glPushMatrix()
            glTranslatef(x,y,z)
            if real:
                glColor4f(0,0,0,d.blue)
            else:
                glColor3b(d.color_id.red, d.color_id.green, d.color_id.blue)
            glCallList(self.listHexBody)
            glPopMatrix()
        
        if real:
            if self.recording:
                self.save_image(image=False)
            self.frameno += 1

    def set3dProjection(self, real=True):
        core._BaseSimulatorWidget.set3dProjection(self, real)
        gluPerspective(45.0,float(self.width())/self.height(),0.1,200.0)    #setup lens
        glTranslatef(0, 0, -150.0)                #move back
        #glRotatef(60, 1, 60, 90)                       #orbit higher
        glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)

def wall_graphics(cloud):
    core._simulator_graphics(cloud, _WallGLWidget)
