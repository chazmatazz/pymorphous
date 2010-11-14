from pymorphous import *

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *



#some simple data for a colored cube
#here we have the 3D point position and color
#for each corner. then we have a list of indices
#that describe each face, and a list of indieces
#that describes each edge


CUBE_POINTS = (
    (0.5, -0.5, -0.5),  (0.5, 0.5, -0.5),
    (-0.5, 0.5, -0.5),  (-0.5, -0.5, -0.5),
    (0.5, -0.5, 0.5),   (0.5, 0.5, 0.5),
    (-0.5, -0.5, 0.5),  (-0.5, 0.5, 0.5)
)

#colors are 0-1 floating values
CUBE_COLORS = (
    (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 0),
    (1, 0, 1), (1, 1, 1), (0, 0, 1), (0, 1, 1)
)

CUBE_QUAD_VERTS = (
    (0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4),
    (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6)
)

RGB_COLORS = [(
    (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0),
    (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0)
),(
    (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0),
    (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0)
),(
    (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1),
    (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1)
)]

def blit(cloud):
    "draw the program"
    for d in cloud.devices:
        glPushMatrix()
        glTranslatef(d.x*20, d.y*20, d.z*20)
    
        allpoints = zip(CUBE_POINTS, CUBE_COLORS)
    
        glBegin(GL_QUADS)
        for face in CUBE_QUAD_VERTS:
            for vert in face:
                pos, color = allpoints[vert]
                glColor3fv(color)
                glVertex3fv(pos)
        glEnd()
        glPopMatrix()
        
        for i in range(3):
            if d.leds[i] != 0:
                glPushMatrix()
                glTranslatef(d.x*20, d.y*20, d.z*20+d.leds[i])
            
                allpoints = zip(CUBE_POINTS, RGB_COLORS[i])
            
                glBegin(GL_QUADS)
                for face in CUBE_QUAD_VERTS:
                    for vert in face:
                        pos, color = allpoints[vert]
                        glColor3fv(color)
                        glVertex3fv(pos)
                glEnd()
                glPopMatrix()
     
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
        

    
