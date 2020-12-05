import pygame
from random import *
from pygame.locals import *
from math import *
from vector import *
import sys
import os
import json
pygame.init()
screen = pygame.display.set_mode((500,500))

TILESIZE = 22
TILENUM = 16
FILENAME = "rooms.json"
#function to get all the rooms as text representation from the file and store in a list
def getrooms():
    #raise exception if file to read from cannot be found
    if not os.path.exists(FILENAME):
        file = open(FILENAME,"w")
        rooms = {"stage1":{"spawn":[{"tiles": [[1,(0,0)]]}]}}
        json.dump(rooms,file,sort_keys=True)
        file.close()
    #opens file in read mode
    file = open(FILENAME,"r")
    roomdict = json.load(file)
    
    file.close()
    return roomdict

#writes the dictionary to the file in format
def writefile(rooms=[]):
    #clear existing file
    file = open(FILENAME,"w")

    #stage>roomtype>room=,enemies,items,tiles,directions
    #tiles=[[tileid,pos], ...]
    
    #rooms = {"stage1":{"spawn":[{"tiles": [[1,(0,0)]]}]}}
    
    json.dump(rooms,file,sort_keys=True)
    file.close()
#writefile()
    
#object for a single room of a map
class Room:
    def __init__(self,room):
        #list to store tile objects
        tiles = room["tiles"]
        try:
            self.enemies = room["enemies"]
        except:
            self.enemies = []
        self.completed = False
        if self.enemies == []:
            self.completed = True
            
        self.tilelist = []
        self.visualtiles = []
        for tile in tiles:
            #tileid = tile[0]
            
            tilepos = vector(tile[1])
            tileid = tile[0]
            abovetile,belowtile,lefttile,righttile = False,False,False,False
            
            abovepos = vector(tile[1])+vector(0,-1)
            belowpos = vector(tile[1])+vector(0,1)
            leftpos = vector(tile[1])+vector(-1,0)
            rightpos = vector(tile[1])+vector(1,0)
            for tile2 in tiles:
                abovetile = abovetile or tile2[1] == abovepos
                belowtile = belowtile or tile2[1] == belowpos
                lefttile = lefttile or tile2[1] == leftpos
                righttile = righttile or tile2[1] == rightpos
            
            placedict = {"top":[abovetile,abovepos],
                         "bottom":[belowtile,belowpos],
                         "left":[lefttile,leftpos],
                         "right":[righttile,rightpos]}

            tiletype = "stonetile"
            keys = SURFACES.keys()
            if tileid == 1:
                tiletype = "stonetile"
                if not abovetile and tilepos[1]!=0:
                    tiletype = "grasstile"
                    if randint(0,1)==1:
                        self.visualtiles.append(Tile(abovepos,"grasstiledecor1top"))

                for key in placedict:
                    contents = placedict[key]
                    if contents[0] != True:
                        if tiletype+key in keys:
                            self.visualtiles.append(Tile(contents[1],tiletype+key))
            if tileid == 2:
                tiletype = "gatetile"
            self.tilelist.append(Tile(tilepos,tiletype))
                
                    
                    

            
    #draws all the tiles in the room
    def update(self,surf):
        """
        for tile in self.tilelist:
            tile.update(surf)
        """
        for tile in self.tilelist:
            tile.update(surf)

    def updatedecor(self,surf):
        for tile in self.visualtiles:
            tile.update(surf)
    #returns a list of all the tile objects
    def getenemies(self):
        return self.enemies
    
def returnsprites(spritesheet,dictionary):
    newdict = {}
    for key in dictionary:
        contents = dictionary[key]
        surf = pygame.Surface(contents.size)
        surf.blit(spritesheet,-vector(contents.topleft))
        
        tempsurf = pygame.Surface((TILESIZE,TILESIZE))
        tilerect = pygame.Rect(0,0,TILESIZE,TILESIZE)
        temprect = surf.get_rect()
        if key[-3:]=="top":
            temprect.bottom = tilerect.bottom
            tempsurf.blit(surf,temprect)
            surf = tempsurf
        if key[-4:]=="left":
            temprect.right = tilerect.right
            tempsurf.blit(surf,temprect)
            surf = tempsurf
        if key[-5:]=="right":
            temprect.left = tilerect.left
            tempsurf.blit(surf,temprect)
            surf = tempsurf
        if key[-6:]=="bottom":
            temprect.top = tilerect.top
            tempsurf.blit(surf,temprect)
            surf = tempsurf
        if not key[-4:]=="tile":
            surf.set_colorkey((0,0,0))
        surf.convert()
        newdict[key] = surf
    return newdict

        
#object for tiles
spritesheet = pygame.image.load("sprites/rocktiles.png")
SURFACES = {"grasstile":pygame.Rect(4,6,22,22),
            "grasstiledecor1top":pygame.Rect(4,0,22,5),
            "grasstileleft":pygame.Rect(0,6,3,22),
            "grasstileright":pygame.Rect(27,6,3,22),
            "grasstilebottom":pygame.Rect(4,52,22,1),
            "stonetile":pygame.Rect(4,29,22,22),
            "stonetileright":pygame.Rect(2,29,1,22),
            "stonetileleft":pygame.Rect(27,29,1,22),
            "stonetilebottom":pygame.Rect(4,52,22,1)
            }
SURFACES = returnsprites(spritesheet,SURFACES)
SURFACES["gatetile"] = pygame.Surface((TILESIZE,TILESIZE))
SURFACES["gatetile"].fill((255,0,0))


"""
newsurface = pygame.Surface((22,22))
newsurface.blit(spritesheet,-vector(4,29))
surfaces["stonetile"] = newsurface
newsurface = pygame.Surface((22,22))
newsurface.blit(spritesheet,-vector(4,5))
SURFACES["grasstile"] = newsurface

"""
class Tile:
    def __init__(self,pos,tileid=None):
        #if no image is given, set it to a red square
        if tileid==None or tileid==1:
            self.image = "stonetile"
        elif tileid == "gatetile" or tileid == 2:
            self.image = "gatetile"
        else:
            self.image=tileid
        #get the hitbox from the image
        self.rect = SURFACES[self.image].get_rect()
        #put the hitbox at the given position using its topleft position
        self.rect.topleft = vector(pos)*TILESIZE
    #draws the tile
    def update(self,surf):
        surf.blit(SURFACES[self.image],self.rect)

