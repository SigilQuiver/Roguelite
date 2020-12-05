#this module contains the player class
import pygame
from pygame.locals import *

import sys
from random import *

import map1 as m
import room1 as r

from vector import *

pygame.init()

screen = pygame.display.set_mode((500,500),pygame.RESIZABLE)

#this module creates constants for the gravity and maximum vertical velocity 
GRAVITY = 0.4
MAXY = 10
def outline(image):
    
    poss = [[0,1],[1,0],[2,1],[1,2],[1,1]]
    mask = pygame.mask.from_surface(image)
    newimage = pygame.Surface(vector(image.get_size())+vector(2,2),pygame.SRCALPHA)
    newimage.fill((0,0,0,0))
    outlinelist = mask.outline()
    outlinemask = pygame.Mask(image.get_size())
    for coord in outlinelist:
        outlinemask.set_at(coord,1)
    surf = outlinemask.to_surface(unsetcolor=(0,0,0,0),setcolor=(0,0,0,255))
    for pos in poss:
        newimage.blit(surf,pos)
    return newimage
    
def getdictfromimage():
    spritesheet = pygame.image.load("sprites/idle_run_jump_AA.png").convert_alpha()
    dims = vector(13,26)
    spritelist = []
    for x in range(int(spritesheet.get_width()//dims[0])):
        newimage = pygame.Surface(dims,pygame.SRCALPHA)
        newimage.fill((0,0,0,0))
        newimage.convert_alpha()
        newimage.blit(spritesheet,(-(x*dims[0]),0))
        imgoutline = outline(newimage)
        #newimage.blit(imgoutline,(0,0))
        newimage.convert_alpha()

        finalimage = pygame.Surface(vector(imgoutline.get_size())-vector(0,1),pygame.SRCALPHA)
        finalimage.fill((0,0,0,0))
        finalimage.convert_alpha()
        finalimage.blit(imgoutline,(0,0))
        finalimage.blit(newimage,(1,1))
        spritelist.append(finalimage)
    imagedict = {
        "idle":[],
        "walk":[]
        }
    imagedict["idle"] = spritelist[0:4]
    imagedict["walk"] = spritelist[4:8]
    imagedict["jumpup"] = [spritelist[8]]
    imagedict["jumpdown"] = [spritelist[9]]
    return imagedict

class Player:
    def __init__(self):
        #loads in the hitbox and image for the player
        self.state = "idle"
        
        self.dims = vector(13,26)

        self.dictimage = getdictfromimage()
        
        self.image = pygame.Surface(self.dictimage[self.state][1].get_size())
        self.image.fill((0,255,0))
        self.image.convert()
        
        self.rect = self.image.get_rect()
        self.rect.center += vector(r.TILESIZE,r.TILESIZE)
        
        self.velocity = [0.1,0.1]
        self.gravity = GRAVITY
        self.maxy = MAXY
        self.speed = 2 
        self.jumpheight = 7
        self.minheight = 1

        #the Timer class counts frames
        #used for a jump buffer
        self.canjump = False
        self.jumpbuffer = Timer(8)

        #used when jumping
        self.jumptimer = Timer(11)
        self.jumping = False

        self.direction = "left"
        self.animtimer = Timer(12)
        self.pos = list(self.rect.center)
        self.deltax = 0

        self.shotspeed = 3
        self.shootspeed = 20
        self.shoottimer = Timer(self.shootspeed)

        self.maxhp = 6
        self.hp = 6

        self.invunerable = False
        self.invuntimer = Timer(200)
        self.invunflash = False
        self.invunflashtimer = Timer(15)

        self.hastriedshot = False
        
    def damage(self):
        if not self.invunerable:
            self.hp -=1
            self.invunerable = True
            self.invuntimer.reset()
    def updateinvun(self):
        if self.invunerable:
            if self.invuntimer.update():
                self.invunerable = False
            if self.invunflashtimer.update():
                self.invunflash = not self.invunflash
        if not self.invunerable:
            self.invunflash = False
    def update(self,tilelist,surface,keys):
        self.keyupdate(keys)
        self.updatecollide(tilelist)
        self.updatesprite(surface)
        self.updateinvun()
        if not self.hastriedshot:
            self.shoottimer.update()
        else:
            self.hastriedshot = False
    def canshoot(self):
        self.hastriedshot = True
        if self.shoottimer.update():
            self.shoottimer.reset()
            return True
            
    def updatecollide(self,tilelist):
        self.deltax = self.pos[0]
        #adds the x velocity, then checks if a tile collision occurs
        self.pos[0] += self.velocity[0]
        self.rect.center = self.pos
        #if a collision does occur, move the player out of the tile, based on the velocity of the player
        for tile in tilelist:
            rect = tile.rect
            if self.rect.colliderect(tile):
                if self.velocity[0] > 0:
                    self.rect.right = rect.left
                else:
                    self.rect.left = rect.right
                self.pos = list(self.rect.center)
        self.deltax  = abs(self.deltax-self.pos[0])
        #adds the y velocity, then checks if a tile collision occurs
        self.velocity[1] = min(self.velocity[1],self.maxy)
        self.pos[1] += self.velocity[1]
        self.rect.center = self.pos
        #if a collision does occur, move the player out of the tile, based on the velocity of the player
        startbuffer = False
        for tile in tilelist:
            rect = tile.rect
            if self.rect.colliderect(tile):
                self.jumpbuffer.reset()
                #if the player lands on the ground
                if self.velocity[1] > 0 :
                    self.velocity[1] = 0
                    self.rect.bottom = rect.top
                    #allow the player to jump
                    self.canjump = True
                    self.jumping = False
                #if the player hits a celing
                else:
                    self.rect.top = rect.bottom
                    #set their y velocity to 0
                    self.velocity[1] = 0
                    self.jumping = False
                    self.jumptimer.reset()
                self.pos = list(self.rect.center)
            else:
                startbuffer = True
                
        if startbuffer:
            if self.jumpbuffer.update():
                self.canjump = False
            
        self.velocity[1] += self.gravity
    def keyupdate(self,keys):
        #if the player is on the ground or in a jump buffer, start a jump
        if K_w in keys and self.canjump and not self.jumping:
            self.jumping = True
            self.jumpperc = 0
            self.velocity[1] = 0
            self.canjump = False
            self.jumptimer.reset()

        #if w is held from the start of the jump
        if K_w in keys and self.jumping:
            #if the player has not reached the maximum jump height from holding w
            if not self.jumptimer.update():
                #increase the velocity by using lerp
                self.jumpperc += 1/self.jumptimer.maxtimer
                self.velocity[1] = lerp(-self.jumpheight,-self.minheight,self.jumpperc)
            else:
                self.jumping = False
                
        #if w has stopped being held and the player is jumping
        if self.jumping and not K_w in keys:
            self.jumping = False
        #if the player is not jumping, remove the w input from the existing keys
        if not self.jumping:
            try:
                keys.remove(K_w)
            except:
                pass
            
        #when the player starts to walk left or right, the velocity gradually increases over a short period of time up to the maximum walking speed
        #the speed at which velocity is gained
        slip = 0.7
        
        if K_a in keys:
            self.direction = "left"
            self.velocity[0] = -self.speed#lerp(self.velocity[0],-self.speed,-slip)
        elif K_d in keys:
            self.direction = "right"
            self.velocity[0] = self.speed#lerp(self.velocity[0],self.speed,slip)
        else:
            self.velocity[0] = 0
    #draws the sprite for the player
    def updatesprite(self,surface):
        state = None
        
        image = self.image
        if self.canjump:
            normaltimer = 12
            if self.velocity[0]==0:
                self.animtimer.changemax(normaltimer)
            else:
                self.animtimer.changemax(normaltimer/abs(self.velocity[0]))
            if self.velocity[0] != 0:
                state = "walk"
            else:
                state = "idle"
        else:
            if self.velocity[1] <= 0:
                state = "jumpup"
            if self.velocity[1] > 0:
                state = "jumpdown"
        
        if self.animtimer.update():
            self.animtimer.reset()
            if state != None:
                self.dictimage[state].append(self.dictimage[state].pop(0))
            
        if state != None:
            image = self.dictimage[state][0]
        else:
            image = self.image
            
        if self.direction != "right":
            image = pygame.transform.flip(image,True,False)
        if not self.invunflash:
            surface.blit(image,self.rect)
    def updatepos(self):
        self.pos = list(self.rect.center)

                

        
            
