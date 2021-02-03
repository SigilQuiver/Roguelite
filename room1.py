import pygame
from random import *
from pygame.locals import *
from math import *
from vector import *
import sys
import os
import json
from text import *
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
        #get all the tiles from a room dictionary
        tiles = room["tiles"]

        #a room won't guaranteed have enemies, so if it doesn't set the enemies to be spawned to none
        try:
            self.enemies = room["enemies"]
        except:
            self.enemies = []

        #if there are no enemies already in the room, mark the room as completed
        self.completed = False
        if self.enemies == []:
            self.completed = True

        #tiles in tilelist are collideable tiles, tiles in visual tiles are for decor
        self.tilelist = []
        self.visualtiles = []

        #loop through all the tiles in list representation ([tile pos,tile type])
        for tile in tiles:
            tilepos = vector(tile[1])
            tileid = tile[0]

            #gets if the positions above,below,to the left and to the right also contain a tile
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

            #gets the adjacent positions, above, below and to the sides of the current tiles position
            placedict = {"top":[abovetile,abovepos],
                         "bottom":[belowtile,belowpos],
                         "left":[lefttile,leftpos],
                         "right":[righttile,rightpos]}

            #applys decor based on adjacent tiles.
            #each tile texture has a name, if the name has top,bottom,left or right and the name of the tile it will join to,
            #it will be automatically assigned to the respective position if there is not a tile there
            #tile textures with the name decor in it are applied on an individual basis
            tiletype = "stonetile"
            keys = SURFACES.keys()

            #set tile textures based on id(the tile type from [tile pos, tile type]), and apply decor individually on top based on random probability
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
            if tileid == 3:
                tiletype = "bulletground"
                
            #automatically apply any, top, bottom, left or right textures to a tile
            if type(tileid)==type(int(1)):
                for key in placedict:
                    contents = placedict[key]
                    if contents[0] != True:
                        if tiletype+key in keys:
                            self.visualtiles.append(Tile(contents[1],tiletype+key))

            #if the tile is a door instead of a normal tile, create a door object rather than a tile object
            if tileid == "door" or tiletype == "door":
                self.tilelist.append(Door(tilepos,tiletype))
            else:
                self.tilelist.append(Tile(tilepos,tiletype))


            
    #draws all the tiles in the room
    def update(self,surf,player=None,keys=[],inencounter=True,entities=None):
        toreturn = False
        for tile in self.tilelist:
            if tile.image == "door":
                toreturn = tile.update(surf,player,keys,inencounter,entities)
            else:
                tile.update(surf)
        return toreturn
    
    #draws all decor tiles onto the room
    def updatedecor(self,surf):
        for tile in self.visualtiles:
            tile.update(surf)
            
    #returns a list of where to spawn enemies and what type of enemy should be spawned
    def getenemies(self):
        return self.enemies
    #returns a lost of the tile objects
    def gettiles(self):
        return self.tilelist

#takes in a dictionary of pygame Rects and a sprite sheet
#returns the same dictionary except for each key there is an image instead for the rect's position on the spritesheet
#for some decor tiles, their dimensions do not match that of a normal tile (22,22), and so they are
#anchored to whichever direction was specified in its name
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

        
#fetches all the tiles and puts them into the constant SURFACES
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
SURFACES["bulletground"] = pygame.image.load("sprites/bulletground.png").convert()


#an object used to store the image and collider for a single tile
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
    #draws the tile to the screen
    def update(self,surf):
        surf.blit(SURFACES[self.image],self.rect)
    def getrect(self):
        return rect

#an object used by the player to move into the next stage, it acts similarly to a tile, but can't be collided with the player
class Door:
    def __init__(self,bottompos,tileid=None):
        self.image = "door"
        self.rect = pygame.Rect((-1,-1),(1,1))
        self.bottomrect = pygame.Rect((0,0),(22,22))
        self.bottomrect.topleft = vector(bottompos)*TILESIZE
        #the door only appears once all enemies in the current room have been defeated
        self.washidden = False

    def update(self,surf,player,keys,completed,entities):
        #some of the parameters will be equal to None, this is because in some cases (such as the tile editor)
        #where I can't pass in the player or entities objects and just want the image
        
        toreturn = False
        #only draw the door when the room is completed
        if completed:
            #check this is the first time the door is drawn
            if self.washidden and entities != None:
                #effects for the door appearing
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

            
                
            if player != None:
                #if the player is touching the door
                if imagerect.colliderect(player.getrect()):
                    #put a text prompt above the player
                    textimage = generatetext("press R to go to the next stage",None,"small",(0,0),(192,192,192))
                    textback = pygame.Surface(textimage.get_size())
                    textback.blit(textimage,(0,0))
                    textrect = textback.get_rect()
                    textrect.centerx = imagerect.centerx
                    textrect.bottom = imagerect.top+-5
                    surf.blit(textback,textrect)
                    
            #if the player presses the key in the prompt
            if K_r in keys:
                keys.remove(K_r)
                toreturn = True
                
        else:
            #if the room isn't completed, use a variable to keep track of this for the effects
            #that happen when the door first appears
            self.washidden = True

        #returns true if the player pressed the key that the prompt was asking for
        #this is used elsewhere in the code to change stages
        return toreturn

