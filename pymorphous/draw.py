from pymorphous import *

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def blit(cloud):
    "draw the program"
    def drawDevice(d):
        x = d.x*20
        y = d.y*20
        z = d.z*20
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
                
    map(drawDevice, cloud.devices)
     
def spawn_cloud(*args, **kwargs):
    "run the program"

    cloud = Cloud(*args, **kwargs)
    
    #initialize pygame and setup an opengl display    
    pygame.init()
    pygame.display.set_mode((cloud.width,cloud.height), OPENGL|DOUBLEBUF)
    glEnable(GL_DEPTH_TEST)        #use our zbuffer

    #setup the camera
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45.0,float(cloud.width)/cloud.height,0.1,100.0)    #setup lens
    glTranslatef(0.0, 0.0, -50.0)                #move back
    glRotatef(60, 1, 60, 0)                       #orbit higher

    clock = pygame.time.Clock()
    
    while True:
        time_passed = clock.tick(cloud.desired_fps)
        #check for quit'n events
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break

        #clear screen and move camera
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)                  
        
        #orbit camera around by 1 degree
        #glRotatef(1, 0, 1, 0)   
        
        cloud.update(time_passed)
        blit(cloud)
        pygame.display.flip()
        

    
