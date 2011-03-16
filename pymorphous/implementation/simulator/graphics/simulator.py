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

from pymorphous.implementation.simulator.graphics import core

class _SimulatorGLWidget(core._BaseSimulatorWidget):
    
    def __init__(self, cloud, parent=None):
        core._BaseSimulatorWidget.__init__(self, cloud, parent)
        
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        
        self._wave_cone_cache = {}
        
    def __del__(self):
        self.makeCurrent()

        glDeleteLists(self.listSimpleBody, 1)
        glDeleteLists(self.listSelect, 1)
        glDeleteLists(self.listSelectedDevice, 1)
        glDeleteLists(self.listRadio, 1)
        glDeleteLists(self.listBlendLed, 1)
        for lst in self._wave_cone_cache:
            glDeleteLists(lst, 1)
        for i in range(3):
            glDeleteLists(self.listSenses[i], 1)
        for i in range(3):
            glDeleteLists(self.listLeds[i], 1)

    def initializeGL(self):
        glutInit()
        
        self.listSimpleBody = glGenLists(1)
        if not self.listSimpleBody:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listSimpleBody, GL_COMPILE)
        glutWireSphere(*self.cloud.settings.graphics.simple_body_dim)
        glEndList()
        
        self.listSelect = glGenLists(1)
        if not self.listSelect:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listSelect, GL_COMPILE)
        glutSolidSphere(*self.cloud.settings.graphics.select_dim)
        glEndList()
        
        self.listSelectedDevice = glGenLists(1)
        if not self.listSelectedDevice:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listSelectedDevice, GL_COMPILE)
        glutSolidSphere(*self.cloud.settings.graphics.selected_device_dim)
        glEndList()
        
        self.listRadio = glGenLists(1)
        if not self.listRadio:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listRadio, GL_COMPILE)
        glutSolidSphere(0.8 * 4, 8, 8) # TODO
        glEndList()
        
        self.listBlendLed = glGenLists(1)
        if not self.listBlendLed:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listBlendLed, GL_COMPILE)
        glutSolidSphere(0.8, 8, 8) # TODO
        glEndList()
        
        self.listSenses = []
        for i in range(3):
            self.listSenses += [glGenLists(1)]
            if not self.listSenses[i]:
                raise SystemError("""Unable to generate display list using glGenLists""")
            glNewList(self.listSenses[i], GL_COMPILE)
            glutSolidSphere(*self.cloud.settings.graphics._user_sensor_dims[i])
            glEndList()
            
        self.listLeds = []
        for i in range(3):
            self.listLeds += [glGenLists(1)]
            if not self.listLeds[i]:
                raise SystemError("""Unable to generate display list using glGenLists""")
            glNewList(self.listLeds[i], GL_COMPILE)
            glutSolidSphere(*self.cloud.settings.graphics._led_dims[i])
            glEndList()
            
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        glShadeModel(GL_FLAT)
        self.setMode(True)
        self.set3dProjection()
    
    def get_wave_cone(self, radius):
        try:
            return self._wave_cone_cache[radius]
        except KeyError:
            self._wave_cone_cache[radius] = glGenLists(1)
            if not self._wave_cone_cache[radius]:
                raise SystemError("""Unable to generate display list using glGenLists""")
            glNewList(self._wave_cone_cache[radius], GL_COMPILE)
            gluCylinder(gluNewQuadric(), 1, 0, radius, 10, 10)
            glEndList()
            return self._wave_cone_cache[radius]

    def mousePressEvent(self, event):
        d = self.select_device(event)
        if d:
            if d == self.selected_device:
                self.selected_device = None
            else:
                self.selected_device = d
            
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
        
        if key == QtCore.Qt.Key_I:
            self.save_image()
        if key == QtCore.Qt.Key_R:
            self.recording = True
        if key == QtCore.Qt.Key_S:
            self.recording = False
        sense_keys = [QtCore.Qt.Key_T, QtCore.Qt.Key_Y, QtCore.Qt.Key_U]
        for i in range(len(sense_keys)):
            if key == sense_keys[i]:
                if self.selected_device:
                    self.selected_device.senses[i] = not self.selected_device.senses[i]
                    self.updateGL()
                    
        if key == QtCore.Qt.Key_L:
            self.cloud.show_leds = not self.cloud.show_leds
            self.updateGL()
            
        dirs = {QtCore.Qt.Key_Left: [-1, 0],
                QtCore.Qt.Key_Right: [1, 0],
                QtCore.Qt.Key_Up: [0, 1],
                QtCore.Qt.Key_Down: [0, -1]}
        for (k, v) in dirs.items():
            if key == k:
                glTranslatef(10 * v[0], 10 * v[1], 0)
                self.updateGL()
                
        if key == QtCore.Qt.Key_3:
            self.cloud.led_stacking_mode = (self.cloud.led_stacking_mode + 1) % 3
            self.updateGL()
            
        if key == QtCore.Qt.Key_B:
            self.cloud.show_body = not self.cloud.show_body
            self.updateGL()
            
        if key == QtCore.Qt.Key_W:
            self.cloud.led_wave_wall = not self.cloud.led_wave_wall
            self.updateGL()
        
    def mypaint(self, real):
        self.setMode(real)
        self.set3dProjection()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 

        for d in self.cloud.devices:
            x = d.x
            y = d.y
            z = d.z
            glPushMatrix()
            glTranslatef(x, y, z)
            if real:
                if self.cloud.show_body:
                    glColor4f(*self.cloud.settings.graphics.simple_body_color)
                    glCallList(self.listSimpleBody)
                    for i in range(3):
                        if d.senses[i] != 0:
                            glColor4f(*self.cloud.settings.graphics._user_sensor_colors[i])
                            glCallList(self.listSenses[i])
                    if d == self.selected_device:
                        glColor4f(*self.cloud.settings.graphics.selected_device_color)
                        glCallList(self.listSelectedDevice)
                        
                if self.cloud.show_radio:
                    glColor4f(*self.cloud.settings.graphics.radio_range_ring_color)
                    glCallList(self.listRadio)
                
                if self.cloud.show_leds:
                    if self.cloud.led_wave_wall:
                        glPushMatrix()
                        glRotatef(core._radian_to_deg(d.leds[1]), 0, 0, 1) #theta
                        glRotatef(core._radian_to_deg(d.leds[2]), 0, 1, 0) #phi
                        glColor3f(0.5, 1, 0.5)
                        glCallList(self.get_wave_cone(d.leds[0])) #radius
                        glPopMatrix()
                    elif self.cloud.led_blend:
                        if(d.leds != [0, 0, 0]):
                            glPushMatrix()
                            glTranslatef(0, 0, 0)
                            glColor3f(*d.leds)
                            glCallList(self.listBlendLed)
                            glPopMatrix()
                    else:
                        leds = [0, 0, 0]
                        if not self.cloud.led_flat:
                            if self.cloud.led_stacking_mode == pymorphous.implementation.simulator.constants.LED_STACKING_MODE_DIRECT:
                                acc = 0
                                for i in range(3):
                                    leds[i] = d.leds[i] + acc
                                    acc += d.leds[i]
                            elif self.cloud.led_stacking_mode == pymorphous.implementation.simulator.constants.LED_STACKING_MODE_OFFSET:
                                for i in range(3):
                                    leds[i] = d.leds[i] + i
                            else:
                                for i in range(3):
                                    leds[i] = d.leds[i]
                            
                        for i in range(3):
                            if d.leds[i] != 0:
                                glPushMatrix()
                                glTranslatef(0, 0, leds[i])
                                glColor4f(*self.cloud.settings.graphics._led_colors[i])
                                glCallList(self.listLeds[i])
                                glPopMatrix()
            else:
                if self.cloud.show_body:
                    glColor3b(d.color_id.red, d.color_id.green, d.color_id.blue)
                    glCallList(self.listSelect)
            glPopMatrix()
        if real:
            if self.recording:
                self.save_image(image=False)
            self.frameno += 1
    
    def set3dProjection(self):
	glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        gluPerspective(45.0, float(self.width()) / self.height(), 0.1, 200.0)    #setup lens
        glTranslatef(0, 0, -150.0)                #move back
        #glRotatef(60, 1, 60, 90)                       #orbit higher
        glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)


    def setMode(self, real):
        if real:
            color = self.cloud.settings.graphics.background_color
        else:
            color = (1, 1, 1, 1)
        glClearColor(*color)
  
def simulator_graphics(cloud):
    app = QtGui.QApplication(sys.argv)
    window = core._SimulatorWindow(cloud=cloud, widget=_SimulatorGLWidget)
    window.show()
    sys.exit(app.exec_())
    
