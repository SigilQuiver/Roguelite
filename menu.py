import pygame
from pygame.locals import *

import sys
from random import *

from vector import *

from text import *

pygame.init()

screen = pygame.display.set_mode((300,300),pygame.RESIZABLE)
def changecolour(surf,colour1,colour2):
    surfback = surf.copy()
    surfback.fill((1,2,3))
    surfback.blit(surf,(0,0))
    surfback.set_colorkey(colour1)
    surfback2 = surf.copy()
    surfback2.fill((colour2))
    surfback2.blit(surfback,(0,0))
    surfback2.set_colorkey((1,2,3))
    return surfback2
    

class Quickprint:
    def __init__(self):
        self.printlist = []
    def update(self,screen):
        surfacelist = []
        ypointer=0
        for string in self.printlist:
            surface = textgen.generatetext(string)
            surface = changecolour(surface,(0,0,0),(11,180,11))
            back = surface.copy()
            back.fill((0,0,0))
            back.blit(surface,(0,0))
            surface=back
            rect = surface.get_rect()
            rect.y = ypointer
            rect.right = screen.get_width()
            screen.blit(surface,rect)
            ypointer += rect.height
        self.printlist = []
    def print(self,*strings):
        string = ""
        for x in strings:
            string += str(x)
        self.printlist.append(string+" ")

quick = Quickprint()


class Button:
    def __init__(self,text,pos):
        self.textcolour = (192,192,192)
        self.textimage = textgen.generatetext(text)
        self.textimage = changecolour(self.textimage,(0,0,0),self.textcolour)
        self.colourhighlight = 90
        self.colournormal = 0
        self.actualcolour = self.colournormal
        self.buttonsurface = pygame.Surface((vector(self.textimage.get_size())+vector(1,1)))
        self.rect = self.buttonsurface.get_rect()
        self.rect.topleft = pos
    def update(self,surface,mousepos):
        
        if self.rect.collidepoint(mousepos):
            self.actualcolour = lerp(self.actualcolour,self.colourhighlight,0.9)
        else:
            self.actualcolour = lerp(self.actualcolour,self.colournormal,0.9)
            
        self.buttonsurface.fill((int(self.actualcolour),int(self.actualcolour),int(self.actualcolour)))
        surface.blit(self.buttonsurface,self.rect)
        surface.blit(self.textimage,vector(self.rect.topleft)+vector(1,1))
        
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(mousepos):
            return True
        return False

clock = pygame.time.Clock()

btn1 = Button("cringe",(30,30))
while True:

    for event in pygame.event.get():
        pass
    
    screen.fill((0,0,0))
    clock.tick(90)
    mousepos = pygame.mouse.get_pos()

    btn1.update(screen,mousepos)
    
    pygame.display.flip()
    
    
