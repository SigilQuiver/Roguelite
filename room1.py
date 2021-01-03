import pygame
from random import *
from pygame.locals import *
from math import *
from vector import *
import sys
import os
import json
import text
from surfacemethods import *
pygame.init()
screen = pygame.display.set_mode((500,500))

TILESIZE = 22
TILENUM = 16
FILENAME = "rooms.json"

import entities as e
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

                
            if tileid == 2:
                tiletype = "bricktile"
                if not abovetile and tilepos[1]!=0:
                    prob = randint(0,20)
                    if prob == 1:
                        self.visualtiles.append(Tile(abovepos,"bricktiledecor1top"))
                    if prob in [2,3]:
                        self.visualtiles.append(Tile(abovepos,"bricktiledecor2top"))
                        
            for key in placedict:
                contents = placedict[key]
                if contents[0] != True:
                    if tiletype+key in keys:
                        self.visualtiles.append(Tile(contents[1],tiletype+key))
            if tileid == "door" or tiletype == "door":
                self.tilelist.append(Door(tilepos,tiletype))
            else:
                self.tilelist.append(Tile(tilepos,tiletype))
                
                    
                    

            
    #draws all the tiles in the room
    def update(self,surf,player=None,keys=[],inencounter=True,entities=None):
        """
        for tile in self.tilelist:
            tile.update(surf)
        """
        toreturn = False
        for tile in self.tilelist:
            if tile.image == "door":
                toreturn = tile.update(surf,player,keys,inencounter,entities)
            else:
                tile.update(surf)
        return toreturn
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
spritesheetdict = {"grasstile":pygame.Rect(4,6,22,22),
            "grasstiledecor1top":pygame.Rect(4,0,22,5),
            "grasstileleft":pygame.Rect(0,6,3,22),
            "grasstileright":pygame.Rect(27,6,3,22),
            "grasstilebottom":pygame.Rect(4,52,22,1),
            "stonetile":pygame.Rect(4,29,22,22),
            "stonetileright":pygame.Rect(2,29,1,22),
            "stonetileleft":pygame.Rect(27,29,1,22),
            "stonetilebottom":pygame.Rect(4,52,22,1)
            }
SURFACES = returnsprites(spritesheet,spritesheetdict)

spritesheet = pygame.image.load("sprites/stonetiles.png")
spritesheetdict = {"bricktile":pygame.Rect(8,14,22,22),
                   "bricktileleft":pygame.Rect(6,14,1,22),
                   "bricktileright":pygame.Rect(31,14,1,22),
                   "bricktiledecor1top":pygame.Rect(36,7,22,7),
                   "bricktiledecor2top":pygame.Rect(57,10,22,4)
                   }
toadd = returnsprites(spritesheet,spritesheetdict)
for key in toadd:
    SURFACES[key] = toadd[key]
        

SURFACES["gatetile1"] = pygame.image.load("sprites/gatetile.png")
SURFACES["gatetile1"].convert()
SURFACES["gatetile2"] = pygame.transform.rotate(pygame.image.load("sprites/gatetile.png"),90)
SURFACES["gatetile2"].convert()
SURFACES["door"] = pygame.image.load("sprites/door.png")


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
        elif tileid == 2:
            self.image = "bricktile"
        else:
            self.image=tileid
        #get the hitbox from the image
        self.rect = SURFACES[self.image].get_rect()
        #put the hitbox at the given position using its topleft position
        self.rect.topleft = vector(pos)*TILESIZE
    #draws the tile
    def update(self,surf):
        surf.blit(SURFACES[self.image],self.rect)
        
class Door:
    def __init__(self,bottompos,tileid=None):
        self.image = "door"
        self.rect = pygame.Rect((-1,-1),(1,1))
        self.bottomrect = pygame.Rect((0,0),(22,22))
        self.bottomrect.topleft = vector(bottompos)*TILESIZE
        self.washidden = False

    def update(self,surf,player,keys,inencounter,entities):
        toreturn = False
        if not inencounter:
            if self.washidden and entities != None:
                for _ in range(randint(5,10)):
                    angle = randint(0,360)
                    v1 = vector(15,0)
                    v1.rotate_ip(angle)
                    entities.add(e.Dust(vector(self.bottomrect.center)+v1,3,(0,0),angle,randint(2,3)))
            self.washidden = False
            
            imagerect = SURFACES[self.image].get_rect()
            imagerect.bottom = self.bottomrect.bottom
            imagerect.left = self.bottomrect.left
            surf.blit(SURFACES[self.image],imagerect)
            if K_r in keys:
                toreturn = True
            if player != None:
                if imagerect.colliderect(player.rect):
                    textimage = text.textgen.generatetext("press R to go to the next stage",None,"small",(0,0),(192,192,192))
                    textback = pygame.Surface(textimage.get_size())
                    textback.blit(textimage,(0,0))
                    textrect = textback.get_rect()
                    textrect.centerx = imagerect.centerx
                    textrect.bottom = imagerect.top+-5
                    surf.blit(textback,textrect)
                
        else:
            self.washidden = True
        return toreturn

