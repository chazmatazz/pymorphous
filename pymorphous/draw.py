from pymorphous import *

from PySide import QtCore, QtGui, QtOpenGL

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
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
    def __init__(self, cloud, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        
        self.cloud = cloud
         
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.step)
        timer.start(1000.0/self.cloud.desired_fps)
    
    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(self.cloud.width, self.cloud.height)
    
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
        glRotatef(1, 0, 1, 0)
        for d in self.cloud.devices:
            x = d.x*50
            y = d.y*50
            z = d.z*50
            leds = d.leds
            glPushMatrix()
            glTranslatef(x,y,z)
        
            # Draw a square (quadrilateral)
            glBegin(GL_QUADS)                   # Start drawing a 4 sided polygon
            glColor3f(1.0, 1.0, 1.0)
            glVertex3f(-1.0, 1.0, 0.0)          # Top Left
            glVertex3f(1.0, 1.0, 0.0)           # Top Right
            glVertex3f(1.0, -1.0, 0.0)          # Bottom Right
            glVertex3f(-1.0, -1.0, 0.0)         # Bottom Left
            glEnd()                             # We are done with the polygon
            glPopMatrix()
            
            for i in range(3):
                if leds[i] != 0:
                    glPushMatrix()
                    glTranslatef(x,y,z+leds[i])
                    
                    # Draw a square (quadrilateral)
                    glBegin(GL_QUADS)                   # Start drawing a 4 sided polygon
                    glColor3f(1.0 if i==0 else 0.0, 1.0 if i==1 else 0.0, 1.0 if i==2 else 0.0)
                    glVertex3f(-1.0, 1.0, 0.0)          # Top Left
                    glVertex3f(1.0, 1.0, 0.0)           # Top Right
                    glVertex3f(1.0, -1.0, 0.0)          # Bottom Right
                    glVertex3f(-1.0, -1.0, 0.0)         # Bottom Left
                    glEnd()                             # We are done with the polygon
                    glPopMatrix()
    
    def resizeGL(self, width, height):
        side = min(width, height)
        #glViewport((width - side) / 2, (height - side) / 2, side, side)

        glMatrixMode(GL_PROJECTION)
        
        gluPerspective(45.0,float(self.cloud.width)/self.cloud.height,0.1,200.0)    #setup lens
        glTranslatef(0.0, 0.0, -150.0)                #move back
        glRotatef(60, 1, 60, 90)                       #orbit higher
    
    def step(self):
        self.cloud.update(0.1)
        self.updateGL()    

def spawn_cloud(*args, **kwargs):
    "run the program"

    cloud = Cloud(*args, **kwargs)
    
    app = QtGui.QApplication(sys.argv)

    window = Window(cloud = cloud)
    window.show()
    
    sys.exit(app.exec_())