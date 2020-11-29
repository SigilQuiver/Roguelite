import pygame
from pygame.locals import *

import sys
from random import *

from vector import *

from text import *

screen = pygame.display.set_mode((300,300))
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

