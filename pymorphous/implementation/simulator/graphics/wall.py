import time
from PySide import QtCore, QtGui, QtOpenGL
import sys
import math
import numpy
import random

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
    
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        
    def __del__(self):
        self.makeCurrent()
        
        glDeleteLists(self.listBackgroundCube, 1)
        glDeleteLists(self.listHex, 1)

    def initializeGL(self):
        glutInit()
        
        self.textures = glGenTextures(4)
        self.create_texture(self.cloud.settings.graphics.wall_background_texture, 0)
        self.create_texture(self.cloud.settings.graphics.wall_pdlc_texture, 1)
        self.create_texture(self.cloud.settings.graphics.wall_red_led_texture, 2)
        self.create_texture(self.cloud.settings.graphics.wall_green_led_texture, 3)
        self.background_texture = self.textures[0]
        self.pdlc_texture = self.textures[1]
        self.red_led_texture = self.textures[2]
        self.green_led_texture = self.textures[3]

        self.listBackgroundCube = glGenLists(1)
        if not self.listBackgroundCube:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listBackgroundCube, GL_COMPILE)
        wmax = 150
        glBegin(GL_QUADS)		                # begin drawing a cube

        # Front Face (note that the texture's corners have to match the quad's corners)
        glNormal3f(0, 0, -1)
        
        glTexCoord2f(0, 0)
        glVertex3f(-wmax, -wmax, wmax)	# Bottom Left Of The Texture and Quad
        
        glTexCoord2f(0, 0) 
        glVertex3f(wmax,-wmax, wmax)	# Bottom Right Of The Texture and Quad
        
        glTexCoord2f(1, 1) 
        glVertex3f(wmax, wmax, wmax)	# Top Right Of The Texture and Quad
        
        glTexCoord2f(0, 1) 
        glVertex3f(-wmax, wmax, wmax)	# Top Left Of The Texture and Quad

        # Back Face
        glNormal3f(0, 0, 1)
        glTexCoord2f(1, 0) 
        glVertex3f(-wmax, -wmax, -wmax)	# Bottom Right Of The Texture and Quad
        
        glTexCoord2f(1, 1) 
        glVertex3f(-wmax,  wmax, -wmax)	# Top Right Of The Texture and Quad
        
        glTexCoord2f(0, 1) 
        glVertex3f(wmax,  wmax, -wmax)	# Top Left Of The Texture and Quad
        
        glTexCoord2f(0, 0) 
        glVertex3f(wmax, -wmax, -wmax)	# Bottom Left Of The Texture and Quad

        # Top Face
        glNormal3f(0, -1, 0)
        
        glTexCoord2f(0, 1) 
        glVertex3f(-wmax, wmax, -wmax)	# Top Left Of The Texture and Quad
        
        glTexCoord2f(0, 0) 
        glVertex3f(-wmax, wmax, wmax)	# Bottom Left Of The Texture and Quad
        
        glTexCoord2f(1, 0) 
        glVertex3f(wmax, wmax, wmax)	# Bottom Right Of The Texture and Quad
        
        glTexCoord2f(1, 1) 
        glVertex3f(wmax, wmax, -wmax)	# Top Right Of The Texture and Quad

        # Bottom Face
        glNormal3f(0, 1, 0)
        
        glTexCoord2f(1, 1) 
        glVertex3f(-wmax, -wmax, -wmax)	# Top Right Of The Texture and Quad
        
        glTexCoord2f(0, 1) 
        glVertex3f(wmax, -wmax, -wmax)	# Top Left Of The Texture and Quad
        
        glTexCoord2f(0, 0) 
        glVertex3f(wmax, -wmax, wmax)	# Bottom Left Of The Texture and Quad
        
        glTexCoord2f(1, 0) 
        glVertex3f(-wmax, -wmax, wmax)	# Bottom Right Of The Texture and Quad

        # Right face
        glNormal3f(-1, 0, 0)
        
        glTexCoord2f(1, 0) 
        glVertex3f(wmax, -wmax, -wmax)	# Bottom Right Of The Texture and Quad
        
        glTexCoord2f(1, 1) 
        glVertex3f(wmax, wmax, -wmax)	# Top Right Of The Texture and Quad
        
        glTexCoord2f(0, 1) 
        glVertex3f(wmax, wmax, wmax)	# Top Left Of The Texture and Quad
        
        glTexCoord2f(0, 0) 
        glVertex3f(wmax, -wmax, wmax)	# Bottom Left Of The Texture and Quad

        # Left Face
        glNormal3f(1, 0, 0)
        
        glTexCoord2f(0, 0) 
        glVertex3f(-wmax, -wmax, -wmax)	# Bottom Left Of The Texture and Quad
        
        glTexCoord2f(1, 0) 
        glVertex3f(-wmax, -wmax, wmax)	# Bottom Right Of The Texture and Quad
        
        glTexCoord2f(1, 1) 
        glVertex3f(-wmax, wmax, wmax)	# Top Right Of The Texture and Quad
        
        glTexCoord2f(0, 1) 
        glVertex3f(-wmax, wmax, -wmax)	# Top Left Of The Texture and Quad

        glEnd()                                    # done with the polygon.
        glEndList()
        
        self.listHex = glGenLists(1)
        if not self.listHex:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listHex, GL_COMPILE)
        r = self.cloud.wall_hex_radius
        glBegin(GL_POLYGON)
        glNormal3f(0,0,-1)
        for i in range(6):
           glTexCoord2f(0,0)
           glVertex2d(r*math.sin(i/6.0*2*math.pi),r*math.cos(i/6.0*2*math.pi))
        glEnd()
        glEndList()
        
        self.listRedLed = glGenLists(1)
        if not self.listRedLed:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listRedLed, GL_COMPILE)
        glutSolidSphere(*self.cloud.settings.graphics.wall_red_led_dim)
        glEndList()
        
        self.listGreenLed = glGenLists(1)
        if not self.listGreenLed:
            raise SystemError("""Unable to generate display list using glGenLists""")
        glNewList(self.listGreenLed, GL_COMPILE)
        glutSolidSphere(*self.cloud.settings.graphics.wall_green_led_dim)
        glEndList()

        glClearDepth(1.0)				# Enables Clearing Of The Depth Buffer
        glDepthFunc(GL_LESS)			# The Type Of Depth Test To Do
        glEnable(GL_DEPTH_TEST)
        self.setMode(True)
        self.set3dProjection()
        
        # set up light number 1
        glLightfv(GL_LIGHT1, GL_AMBIENT, [ 1, 1, 1, 1 ]) # white ambient light at half intensity (rgba)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [ 1, 1, 1, 1 ]) # super bright, full intensity diffuse light
        glLightfv(GL_LIGHT1, GL_POSITION,[ 10, 10, 2.0, 1 ]) # position of light (x, y, z, (position of light))
        glEnable(GL_LIGHT1)                             # turn light 1 on.
        
        glEnable(GL_COLOR_MATERIAL)
        
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
    def create_texture(self, filename, index):
        img = Image.open(filename)
        data = img.tostring("raw", "RGBX", 0, -1)
        
        glBindTexture(GL_TEXTURE_2D, self.textures[index])
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)  # scale linearly when image bigger than texture
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_NEAREST)  # scale linearly + mipmap when image smalled than texture
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.size[0], img.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        # 2d texture, 3 colors, width, height, RGB in that order, byte data, and the data.
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, img.size[0], img.size[1], GL_RGBA, GL_UNSIGNED_BYTE, data)
    
    def do_event(self, event, pressure):
        for d in self.cloud.devices:
            d._reset_senses()
        if(pressure > 0):
            selected_device = self.select_device(event)
            if selected_device:
                selected_device.sense0 = pressure
    
    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        self.do_event(event, 1)
    
    def tabletEvent(self, event):
        self.do_event(event, event.pressure())
                
    def keyPressEvent(self, event):
        key = event.key()
        
        if key == QtCore.Qt.Key_I:
            self.save_image()
        if key == QtCore.Qt.Key_R:
            self.recording = True
        if key == QtCore.Qt.Key_S:
            self.recording = False

        dirs = {QtCore.Qt.Key_Left: [-1,0],
                QtCore.Qt.Key_Right: [1,0],
                QtCore.Qt.Key_Up: [0,1],
                QtCore.Qt.Key_Down: [0,-1]}
        for (k,v) in dirs.items():
            if key == k:
                self.yRot -= 10*v[0]
                self.xRot -= 10*v[1]
                self.updateGL()
            
        
        
    def mypaint(self, real):
        self.setMode(real)
        self.set3dProjection()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
        
        if real:
            glPushMatrix()
            glTranslate(0,0,-160)
            glBindTexture(GL_TEXTURE_2D, self.background_texture)
            glColor4f(1, 1, 1, 1)
            glCallList(self.listBackgroundCube)
            glPopMatrix()
        
        for d in self.cloud.devices:
            x = d.x
            y = d.y
            z = d.z
            glPushMatrix()
            glTranslatef(x,y,z)
            if real:
                glBindTexture(GL_TEXTURE_2D, self.pdlc_texture)
                glColor4f(1,1,1,d.blue*self.cloud.settings.graphics.wall_max_opacity)
            else:
                glColor3b(d.color_id.red, d.color_id.green, d.color_id.blue)
            glCallList(self.listHex)
            
            if real:
                # red
                glBindTexture(GL_TEXTURE_2D, self.red_led_texture)
                glColor4f(1,1,1,d.red)
                glPushMatrix()
                glTranslate(*self.cloud.settings.graphics.wall_red_led_offset)
                glCallList(self.listRedLed)
                glPopMatrix()
                
                # green
                glBindTexture(GL_TEXTURE_2D, self.green_led_texture)
                glColor4f(1,1,1,d.green)
                glPushMatrix()
                glTranslate(*self.cloud.settings.graphics.wall_green_led_offset)
                glCallList(self.listGreenLed)
                glPopMatrix()
                
            glPopMatrix()
        if real:
            if self.recording:
                self.save_image(image=False)
            self.frameno += 1

    def setMode(self, real):
        if real:
            glClearColor(*self.cloud.settings.graphics.background_color)
            glEnable(GL_LIGHTING)
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glShadeModel(GL_SMOOTH)
        else:
            glClearColor(1,1,1,1)
            glDisable(GL_LIGHTING)
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_BLEND)
            glShadeModel(GL_FLAT)

    def set3dProjection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluPerspective(45.0,float(self.width())/self.height(),0.1,200)    #setup lens
        glTranslatef(0, 0, -150)                #move back
        #glRotatef(60, 1, 60, 90)                       #orbit higher
        glRotated(self.xRot / 16.0, 1, 0, 0)
        glRotated(self.yRot / 16.0, 0, 1, 0)
        glRotated(self.zRot / 16.0, 0, 0, 1)

        glMatrixMode(GL_MODELVIEW)


def wall_graphics(cloud):
    fmt = QtOpenGL.QGLFormat()
    fmt.setAlpha(True)
    QtOpenGL.QGLFormat.setDefaultFormat(fmt)
    app = QtGui.QApplication(sys.argv)
    window = core._SimulatorWindow(cloud = cloud, widget=_WallGLWidget)
    window.show()
    sys.exit(app.exec_())
