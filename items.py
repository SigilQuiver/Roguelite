import pygame
from pygame.locals import *

import sys,os,time
from random import *
from vector import *
from surfacemethods import *
import room1 as r
import entities as e
#stat types:
#damage
#damage multiplier
#speed(x)
#shot speed
#shot rate
#max health
#actual health
MINID = 1
MAXID = 1

SURFACES = {}
for filename in os.listdir("sprites/items"):
    if filename.endswith(".png"): 
        image = pygame.image.load("sprites/items/"+filename)
        image.convert_alpha()
        imgoutline = outline(image)
        surf = pygame.Surface(vector(image.get_size()),pygame.SRCALPHA)
        surf.blit(imgoutline,(-1,-1))
        surf.blit(image,(0,0))
        SURFACES[filename[:-4]] = surf

class Items:
    def __init__(self):
        self.itemlist = {}
        self.itemtype = type(Item())
        self.collected = []
    def update(self,screen,player,entities,room):
        self.changestats = False
        if room in self.itemlist.keys():
            for item in self.itemlist[room]:
                item.update(screen,player,entities)
                if item.collected and item.finishanimation and item not in self.collected:
                    self.collected.append(item)
                    self.changestats = True
    def add(self,room,pos=(r.TILESIZE,r.TILESIZE),pool=None):
        if room not in self.itemlist.keys():
            self.itemlist[room] = []
        self.itemlist[room].append(Item(randint(MINID,MAXID),pos))
    def reset(self):
        self.itemlist = {}
    def resetcollection(self):
        self.collected = []
    def getstats(self):
        self.statdict = {}
        self.statdict["damage"] = 0
        self.statdict["damage_mult"] = 1
        self.statdict["speed"] = 0
        self.statdict["shot_speed"] = 0
        self.statdict["shot_rate"] = 0
        self.statdict["max_hp"] = 0
        self.statdict["actual_hp"] = 0
        for item in self.collected:
            self.statdict["damage"] += item.damage
            self.statdict["damage_mult"] += item.damage_mult
            self.statdict["speed"] += item.speed
            self.statdict["shot_speed"] += item.shot_speed
            self.statdict["shot_rate"] += item.shot_rate
            self.statdict["max_hp"] += item.max_hp
            self.statdict["actual_hp"] += item.actual_hp
        return self.statdict
            
            
class Item:
    def __init__(self,ident=None,pos=(0,0)):
        if ident == None:
            self.id = 1
        else:
            self.id = ident
        self.pos = pos
        
        self.upanimation = False
        self.upslip = 0.2
        self.uppos = (0,-30)
        self.finishanimation = False

        self.collected = False
        
        self.name = "..."
        self.quote = "..."
        self.description = "..."
        self.damage = 0
        self.damage_mult = 0
        self.speed = 0
        self.shot_speed = 0
        self.shot_rate = 0
        self.max_hp = 0
        self.actual_hp = 0
        
        
        if self.id == 1:
            self.name = "sword"
            self.quote = "how does this work with a gun??"
            self.description = "damage up"
            self.damage = 100
    def update(self,screen,player,entities):
        if not self.finishanimation:
            image = SURFACES[str(self.id)]
            rect = image.get_rect()
            rect.topleft = self.pos
            screen.blit(image,rect)
            
            if self.upanimation:
                self.pos = self.pos.lerp(self.uppos,self.upslip)
                if inttuple(self.pos)==inttuple(self.uppos):
                    self.finishanimation = True
                    for _ in range(randint(5,10)):
                        angle = randint(0,360)
                        v1 = vector(15,0)
                        v1.rotate_ip(angle)
                        entities.add(e.Dust(vector(rect.center)+v1,3,(0,0),angle,randint(2,3)))
                        
            if rect.colliderect(player.rect) and not self.upanimation:
                self.collected = True
                self.upanimation = True
                self.pos = vector(self.pos)
                self.uppos = vector(self.pos)+vector(self.uppos)
        
