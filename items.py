import pygame
from pygame.locals import *

import sys,os,time,math
from random import *
from vector import *
from surfacemethods import *
import room1 as r
import entities as e
import text as t
#stat types:
#damage
#damage multiplier
#speed(x)
#shot speed
#shot rate
#max health
#actual health
MINID = 1
MAXID = 8

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
    def __init__(self,unlocks):
        self.possibleitems = list(range(MINID+1,MAXID+1))
        for num in unlocks.getommitteditems():
            self.possibleitems.remove(num)
        self.itemlist = {}
        self.itemtype = type(Item())
        self.collected = []
    def update(self,screen,player,entities,room):
        self.changestats = False
        if room in self.itemlist.keys():
            for item in self.itemlist[room]:
                item.update(screen,player,entities)
                if item.collected and item.finishanimation and item not in self.collected:
                    possibleitems.remove(item.id)
                    self.collected.append(item)
                    self.changestats = True
    def add(self,room,pos=(r.TILESIZE,r.TILESIZE),pool=None):
        if room not in self.itemlist.keys():
            self.itemlist[room] = []
        self.itemlist[room].append(Item(choice(self.possibleitems),pos))
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
            if item.actual_hp != 0 and not item.givenhp:
                self.statdict["actual_hp"] += item.actual_hp
                item.givenhp = True
        return self.statdict
    
class Itemview:
    def __init__(self):
        self.scroll = 0
    def update(self,screen,rect,items,mousepos,scroll):
        rectdims = rect.size
        itemsurflist = []
        surf = pygame.Surface(rectdims)
        surf.fill((0,0,0))
        mouseitemid = None
        if len(items.collected) != 0:
            for item in items.collected:
                itemsurflist.append(str(item.id))
            itemdim = SURFACES["1"].get_size()[0]
            
            width = rectdims[0]/itemdim
            width = math.ceil(width)
            rows = len(itemsurflist)/width
            rows = math.ceil(rows)
            #print(width,rows)

            
            
            for y in range(rows):
                y = y*itemdim
                for x in range(width):
                    x = x*itemdim
                    
                    pos = len(itemsurflist)-1
                    surf.blit(SURFACES[itemsurflist[pos]],(x,y))
                    mousecheckrect = pygame.Rect(vector(x,y)+vector(rect.topleft),(itemdim,itemdim))
                    if mousecheckrect.collidepoint(mousepos):
                        mouseitemid = int(itemsurflist[pos])
                    itemsurflist.pop(pos)
                    if len(itemsurflist) == 0:
                        break
                if len(itemsurflist) == 0:
                        break
            surf.scroll(0,int(scroll))
            #self.scroll -= 0.03
        screen.blit(surf,rect)

        if mouseitemid != None:
            tempitem = Item(mouseitemid)
            descriptionsurf = pygame.Surface((70,70))
            descriptionsurf.fill((0,0,0))
            string = tempitem.name
            string += "#"
            string += '"'+tempitem.quote+'"#'
            string += tempitem.description
            descriptionsurf = t.generatetext(string,descriptionsurf,"small",(1,1),(192,192,192))
            descrect = descriptionsurf.get_rect()
            descrect.bottomright = mousepos
            if descrect.left <0:
                descrect.left = 0
            screen.blit(descriptionsurf,descrect)
        
        
            
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
        self.givenhp = False
        
        
        if self.id == 1:
            self.name = "sword"
            self.quote = "how does this work with a gun??"
            self.description = "damage up"
            self.damage = 3
        if self.id == 2:
            self.name = "speedrun stopwatch"
            self.quote = "tryhard sweat smh"
            self.description = "shot rate, shot speed and speed up"
            self.speed = 1
            self.shot_rate = 1
            self.shot_speed = 2
        if self.id == 3:
            self.name = "soldier's stim"
            self.quote = "a vector for paradise"
            self.description = "damage and shot rate up"
            self.damage = 2
            self.shot_rate = 2
        if self.id == 4:
            self.name = "mystery meat"
            self.quote = "I don't think that's for eating"
            self.description = "max hp up, take some damage"
            self.actual_hp = -1
            self.max_hp = 6
        if self.id == 5:
            self.name = "life extender mk.5"
            self.quote = "should it be... dripping?"
            self.description = "max hp up, full heal"
            self.max_hp = 4
            self.actual_hp = 100
        if self.id == 6:
            self.name = "shiny spring"
            self.quote = "mach 20 speeds"
            self.description = "shot speed up"
            self.shot_speed = 2
        if self.id == 7:
            self.name = "wanted poster"
            self.quote = "fastest frog killer in the west"
            self.description = "shot speed and shot rate up"
            self.shot_speed = 1
            self.shot_rate = 1
        if self.id == 8:
            self.name = "participation medal"
            self.quote = "shiny!"
            self.description = "all stats up"
            self.shot_speed = 1
            self.shot_rate = 1
            self.speed = 1
            self.damage = 2
            self.max_hp = 2
            self.damage_mult = 0.5
            
            
        
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
        
