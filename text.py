import pygame
from pygame.locals import *

import time
import sys


from random import *

from vector import *

from surfacemethods import *

pygame.init()
screen = pygame.display.set_mode((800,800))
screen.fill((255,255,69))

TEXTSHEET = "sprites/font_sheet.png"

class Textgenerator:
    def __init__(self):
        self.spritesheet = pygame.image.load(TEXTSHEET)
        self.tiledictsmall = {}
        self.tilesizesmall = {}
        self.tiledictbig = {}
        self.tilesizebig = {}
        
        capitalalpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.bigalpha = list(capitalalpha)
        ypointer = 0
        bigletters = ["M","W"]
        for x in range(len(capitalalpha)):
            dimensions = (11,12)
            char = capitalalpha[x]

            if char not in bigletters:
                actualdimensions = (6,12)
            else:
                actualdimensions = (10,12)
            
            xpointer = x*dimensions[0]
            charsurf = pygame.Surface(actualdimensions)
            charsurf.blit(self.spritesheet,-vector(xpointer,ypointer))
            charsurf.set_colorkey((255,255,255))
            charsurf.convert()
            self.tiledictbig[char] = charsurf
            self.tilesizebig[char] = actualdimensions
            
        alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.-,:+'!?0123456789()/_=\\[]*\"<>"
        self.smallalpha = list(alpha)
        ypointer = 12
        dimensions = (6,7)
        small1 = ["!",".","i","'",":"]
        small2 = [",","j","r"]
        big = ["m","w","M","W"]
        
        for x in range(len(alpha)):
            char = alpha[x]
            actualsize = tuple(dimensions)
            if char not in big+small2+small1:
                actualsize = (3,8)
            if char in small2:
                actualsize = (2,8)
            if char in small1:
                actualsize = (1,8)
            if char in big:
                actualsize = (5,8)
            xpointer = x*dimensions[0]
            charsurf = pygame.Surface(actualsize)
            charsurf.blit(self.spritesheet,-vector(xpointer,ypointer))
            charsurf.set_colorkey((255,255,255))
            charsurf.convert()
            self.tiledictsmall[char] = charsurf
            self.tilesizesmall[char] = actualsize
        
    def blitall(self,screen):
        ypointer = 10
        xpointer = 1
        
        for tilekey in self.tiledictsmall:
            tile = self.tiledictsmall[tilekey]
            screen.blit(tile,(xpointer,ypointer))
            xpointer += tile.get_width() +1
            if xpointer > screen.get_rect().right:
                xpointer = 1
                ypointer += tile.get_height()+1
        ypointer += tile.get_height()+1
        xpointer = 1
        for tilekey in self.tiledictbig:
            tile = self.tiledictbig[tilekey]
            screen.blit(tile,(xpointer,ypointer))
            xpointer += tile.get_width()+1

        pygame.display.flip()
        
    def generatetext(self,text,surface = None,texttype = "small",pos = (0,0),colour = (0,0,0)):
        if surface == None:
            surfwidth = 0
            for char in text:
                if texttype == "small":
                    try:
                        surfwidth += self.tilesizesmall[char][0]+1
                    except:
                        surfwidth += self.tilesizesmall["A"][0]+1
                else:
                    try:
                        surfwidth += self.tilesizebig[char][0]+1
                    except:
                        surfwidth += self.tilesizebig["A"][0]+1
            if texttype == "small":
                surface = pygame.Surface((surfwidth,self.tilesizesmall["A"][1]))
            else:
                surface = pygame.Surface((surfwidth+2,self.tilesizebig["A"][1]))
            surface.fill((255,255,255))
            surface.set_colorkey((255,255,255))
            
        else:
            surfwidth = surface.get_width()
            indents = []
            word = []
            xpointer = 0

            indexnum = 0
            for char in text:
                indexnum += 1
                if texttype == "small":
                    if char not in self.smallalpha+[" ","#"]:
                        char = "?"
                    if char not in [" ","#"]:
                        xpointer += self.tilesizesmall[char][0]+1
                        word.append(char)
                        if xpointer > surfwidth:
                            xpointer = 0
                            for char2 in word:
                                xpointer += self.tilesizesmall[char][0]+1
                            if not len(word) > surfwidth:
                                indents.append(indexnum-len(word))
                    if char in [" ","#"]:
                        word = []
                        if char == " ":
                            xpointer += self.tilesizesmall["A"][0]+1
                        if char == "#":
                            xpointer = 0
            indexnum = 0
            textlist = list(text)
            for indent in indents:
                textlist.insert(indent+indexnum,"#")
                indexnum += 1
            text = "".join(textlist)
                
                        
                        

        
        surfwidth = surface.get_width()
        surfheight = surface.get_height()
        xpointer = pos[0]
        ypointer = pos[1]
        for char in text:
            if texttype == "small":
                ytravel = self.tilesizesmall["A"][1]+1
                if char not in self.smallalpha+[" ","#"]:
                    char = "?"
                if char not in [" ","#"]:
                    tile = self.tiledictsmall[char]
                    previousposition = (xpointer,ypointer)
                    xpointer += self.tilesizesmall[char][0]+1
                    if xpointer > surfwidth:
                        xpointer = 0
                        ypointer += ytravel
                        previousposition = (xpointer,ypointer)
                        xpointer += self.tilesizesmall[char][0]+1
                    if colour != (0,0,0):
                        tile = changecolour(tile,(0,0,0),colour)
                    surface.blit(tile,previousposition)
                elif char == "#":
                    xpointer = 0
                    ypointer += ytravel
                    previousposition = (xpointer,ypointer)
                else:
                    xpointer += self.tilesizesmall["A"][0]+1
            else:
                if char.isalpha():
                    char = char.upper()
                ytravel = self.tilesizebig["A"][1]
                if char not in self.bigalpha+[" "]:
                    char = "A"
                if char != " ":
                    tile = self.tiledictbig[char]
                    previousposition = (xpointer,ypointer)
                    if xpointer > surfwidth:
                        xpointer = 0
                        ypointer += ytravel
                        previousposition = (xpointer,ypointer)
                        xpointer += self.tilesizebig[char][0]+1
                    xpointer += self.tilesizebig[char][0]+1
                    
                    if colour != (0,0,0):
                        tile = changecolour(tile,(0,0,0),colour)
                    surface.blit(tile,previousposition)
                else:
                    xpointer += self.tilesizebig["A"][0]
                

        return surface

textgen = Textgenerator()
                    
"""            

text = Textgenerator()

stuff = pygame.Surface((150,150))
stuff.fill((100,100,100))
stuff.set_colorkey((100,100,100))
#text.blitall(stuff)
stuff = text.generatetext("The large fox jumped over a fence or something, I'm not really sure to be honest?!",stuff,"big")

for x in range(3):
    pass
    #stuff = pygame.transform.scale2x(stuff)

stuff = pygame.transform.scale(stuff,inttuple(vector(stuff.get_size())*2))
screen.blit(stuff,(10,10))
pygame.display.flip()
"""

spritesheet = pygame.image.load(TEXTSHEET)
TILEDICTSMALL = {}
TILESIZESMALL = {}
TILEDICTBIG = {}
TILESIZEBIG = {}

capitalalpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
BIGALPHA = list(capitalalpha)
ypointer = 0
bigletters = ["M","W"]
for x in range(len(capitalalpha)):
    dimensions = (11,12)
    char = capitalalpha[x]

    if char not in bigletters:
        actualdimensions = (6,12)
    else:
        actualdimensions = (10,12)
    
    xpointer = x*dimensions[0]
    charsurf = pygame.Surface(actualdimensions)
    charsurf.blit(spritesheet,-vector(xpointer,ypointer))
    charsurf.set_colorkey((255,255,255))
    charsurf.convert()
    TILEDICTBIG[char] = charsurf
    TILESIZEBIG[char] = actualdimensions
    
alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.-,:+'!?0123456789()/_=\\[]*\"<>"
SMALLALPHA = list(alpha)+["£"]
ypointer = 12
dimensions = (6,7)
small1 = ["!",".","i","'",":"]
small2 = [",","j","r"]
big = ["m","w","M","W"]

for x in range(len(alpha)):
    char = alpha[x]
    actualsize = tuple(dimensions)
    if char not in big+small2+small1:
        actualsize = (3,8)
    if char in small2:
        actualsize = (2,8)
    if char in small1:
        actualsize = (1,8)
    if char in big:
        actualsize = (5,8)
    xpointer = x*dimensions[0]
    charsurf = pygame.Surface(actualsize)
    charsurf.blit(spritesheet,-vector(xpointer,ypointer))
    charsurf.set_colorkey((255,255,255))
    charsurf.convert()
    TILEDICTSMALL[char] = charsurf
    TILESIZESMALL[char] = actualsize

spritesheet = pygame.image.load("sprites/coins.png")
coinnum = 0
COINIMAGE = spritesheettolist(spritesheet,2,True)[coinnum]
COINIMAGE_NOOUT = spritesheettolist(spritesheet,2,True,False)[coinnum]
TILEDICTSMALL["£"] = COINIMAGE_NOOUT
TILESIZESMALL["£"] = COINIMAGE_NOOUT.get_size() 

def blitall(screen):
    ypointer = 10
    xpointer = 1
    
    for tilekey in TILEDICTSMALL:
        tile = TILEDICTSMALL[tilekey]
        screen.blit(tile,(xpointer,ypointer))
        xpointer += tile.get_width() +1
        if xpointer > screen.get_rect().right:
            xpointer = 1
            ypointer += tile.get_height()+1
    ypointer += tile.get_height()+1
    xpointer = 1
    for tilekey in TILEDICTBIG:
        tile = TILEDICTBIG[tilekey]
        screen.blit(tile,(xpointer,ypointer))
        xpointer += tile.get_width()+1

    pygame.display.flip()
        
def generatetext(text,surface = None,texttype = "small",pos = (0,0),colour = (0,0,0)):
    if surface == None:
        surfwidth = 0
        for char in text:
            if texttype == "small":
                try:
                    surfwidth += TILESIZESMALL[char][0]+1
                except:
                    surfwidth += TILESIZESMALL["A"][0]+1
            else:
                try:
                    surfwidth += TILESIZEBIG[char][0]+1
                except:
                    surfwidth += TILESIZEBIG["A"][0]+1
        if texttype == "small":
            surface = pygame.Surface((surfwidth,TILESIZESMALL["A"][1]))
        else:
            surface = pygame.Surface((surfwidth+2,TILESIZEBIG["A"][1]))
        surface.fill((255,255,255))
        surface.set_colorkey((255,255,255))
        
    else:
        surfwidth = surface.get_width()
        indents = []
        word = []
        xpointer = 0

        indexnum = 0
        for char in text:
            indexnum += 1
            if texttype == "small":
                if char not in SMALLALPHA+[" ","#"]:
                    char = "?"
                if char not in [" ","#"]:
                    xpointer += TILESIZESMALL[char][0]+1
                    word.append(char)
                    if xpointer > surfwidth:
                        xpointer = 0
                        for char2 in word:
                            xpointer += TILESIZESMALL[char][0]+1
                        if not len(word) > surfwidth:
                            indents.append(indexnum-len(word))
                if char in [" ","#"]:
                    word = []
                    if char == " ":
                        xpointer += TILESIZESMALL["A"][0]+1
                    if char == "#":
                        xpointer = 0
        indexnum = 0
        textlist = list(text)
        for indent in indents:
            textlist.insert(indent+indexnum,"#")
            indexnum += 1
        text = "".join(textlist)
            
                    
                    

    
    surfwidth = surface.get_width()
    surfheight = surface.get_height()
    xpointer = pos[0]
    ypointer = pos[1]
    for char in text:
        if texttype == "small":
            ytravel = TILESIZESMALL["A"][1]+1
            if char not in SMALLALPHA+[" ","#"]:
                char = "?"
            if char not in [" ","#"]:
                tile = TILEDICTSMALL[char]
                previousposition = (xpointer,ypointer)
                xpointer += TILESIZESMALL[char][0]+1
                if xpointer > surfwidth:
                    xpointer = 0
                    ypointer += ytravel
                    previousposition = (xpointer,ypointer)
                    xpointer += TILESIZESMALL[char][0]+1
                if colour != (0,0,0):
                    tile = changecolour(tile,(0,0,0),colour)
                surface.blit(tile,previousposition)
            elif char == "#":
                xpointer = 0
                ypointer += ytravel
                previousposition = (xpointer,ypointer)
            else:
                xpointer += TILESIZESMALL["A"][0]+1
        else:
            if char.isalpha():
                char = char.upper()
            ytravel = TILESIZEBIG["A"][1]
            if char not in BIGALPHA+[" "]:
                char = "A"
            if char != " ":
                tile = TILEDICTBIG[char]
                previousposition = (xpointer,ypointer)
                if xpointer > surfwidth:
                    xpointer = 0
                    ypointer += ytravel
                    previousposition = (xpointer,ypointer)
                    xpointer += TILESIZEBIG[char][0]+1
                xpointer += TILESIZEBIG[char][0]+1
                
                if colour != (0,0,0):
                    tile = changecolour(tile,(0,0,0),colour)
                surface.blit(tile,previousposition)
            else:
                xpointer += TILESIZEBIG["A"][0]
            

    return surface

