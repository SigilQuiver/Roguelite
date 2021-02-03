import pygame
from pygame.locals import *

import sys,os,time,math
from random import *
from vector import *
from surfacemethods import *
import room1 as r
import entities as e
import text as t

MINID = 1
MAXID = 8

#get all the images from the directory "sprites/items" the images' name corresponds to it's id (e.g.: 1.png is for item id 1)
SURFACES = {}
for filename in os.listdir("sprites/items"):
    if filename.endswith(".png"):
        #each image is given an outline first before being assigned to the image dictionary
        image = pygame.image.load("sprites/items/"+filename)
        image.convert_alpha()
        imgoutline = outline(image)
        surf = pygame.Surface(vector(image.get_size()),pygame.SRCALPHA)
        surf.blit(imgoutline,(-1,-1))
        surf.blit(image,(0,0))
        #the image's id name is the name of the file it was retrieved from minus the ".png"
        SURFACES[filename[:-4]] = surf

#class for storing and updating items
class Items:
    def __init__(self,unlocks):
        self.possibleitems = list(range(MINID+1,MAXID+1))
        for item in unlocks.getommitteditems():
            self.possibleitems.remove(item)
        self.itemlist = {}
        self.itemtype = type(Item())
        self.collected = []
    def update(self,screen,player,entities,room,specialrooms,coins,keys):
        #checks if the room the player is in is a shop room
        for key in specialrooms:
            if specialrooms[key] == "shop":
                shoproom = key
        isshop = False
        if shoproom == room:
            isshop = True
        
        self.changestats = False
        if room in self.itemlist.keys():
            #gets all the items stored in the player's current room,
            for item in self.itemlist[room]:
                item.update(screen,player,entities,isshop,coins,keys)
                #if the item has touched the player and finished it's collected animation, put it in collected list
                #since a new item has been collected, the player needs to update their stats
                if item.collected and item.finishanimation and item not in self.collected:
                    self.collected.append(item)
                    self.changestats = True

    #adds a random item from the pool into the specified room, at the specified position
    def add(self,room,pos=(r.TILESIZE,r.TILESIZE)):
        if room not in self.itemlist.keys():
            self.itemlist[room] = []
        itemid = choice(self.possibleitems)
        self.itemlist[room].append(Item(itemid,pos))
    #removes any leftover items on the current stage
    def reset(self):
        self.itemlist = {}
    #resets the player's collection of items
    def resetcollection(self):
        self.collected = []
    #gets the sum of all the items' stats
    def getstats(self):
        #the stats will be added onto the player's existing stats, so the stats start at 0
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

#UI for the items
class Itemview:
    def __init__(self):
        self.scroll = 0
    def update(self,screen,rect,items,mousepos,scroll):
        #the rect passed into the method is the exact position and shape of the place where the item will be viewed
        rectdims = rect.size
        itemsurflist = []
        surf = pygame.Surface(rectdims)
        surf.fill((0,0,0))
        mouseitemid = None
        if len(items.collected) != 0:
            #get images for all the items the player currently has
            for item in items.collected:
                itemsurflist.append(str(item.id))
            itemdim = SURFACES["1"].get_size()[0]

            #gets how may items can fit in the width and height of the rect
            width = rectdims[0]/itemdim
            width = math.ceil(width)
            rows = len(itemsurflist)/width
            rows = math.ceil(rows)

            #loops through the places the items can go, going left to right,top first
            for y in range(rows):
                y = y*itemdim
                for x in range(width):
                    x = x*itemdim

                    #draw the item to the item UI with all the other items
                    pos = len(itemsurflist)-1
                    surf.blit(SURFACES[itemsurflist[pos]],(x,y))
                    #checks if the mouse is hovering over an item
                    mousecheckrect = pygame.Rect(vector(x,y)+vector(rect.topleft),(itemdim,itemdim))
                    if mousecheckrect.collidepoint(mousepos):
                        mouseitemid = int(itemsurflist[pos])
                    itemsurflist.pop(pos)
                    if len(itemsurflist) == 0:
                        break
                if len(itemsurflist) == 0:
                        break
            #scroll the image down
            surf.scroll(0,int(scroll))
        #draw the item UI to the screen
        screen.blit(surf,rect)

        #if the mouse was hovering over an item on the UI
        if mouseitemid != None:
            
            tempitem = Item(mouseitemid)
            #create a blank black image to put text on
            descriptionsurf = pygame.Surface((70,70))
            descriptionsurf.fill((0,0,0))
            #get the name,description and flavourtext(quote) of the item
            #the hashes added onto the string represent returns
            string = tempitem.name
            string += "#"
            string += '"'+tempitem.quote+'"#'
            string += tempitem.description

            #draw the text image onto the blank black image
            descriptionsurf = t.generatetext(string,descriptionsurf,"small",(1,1),(192,192,192))
            descrect = descriptionsurf.get_rect()
            #put the bottom right of the black image where the mouse is
            descrect.bottomright = mousepos
            #if the image would go offscreen, move it back onscreen
            if descrect.left <0:
                descrect.left = 0
            #draw the black image with text onto the screen
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

        #set all stats to default valuees
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
        self.cost = 180

        #
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
            
            
        
    def update(self,screen,player,entities,isshop,coins,keys):
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
                if isshop:
                    if rect.colliderect(player.rect):
                        if (coins.money-self.cost) >= 0:
                            text = "press R to get item for " +str(self.cost)+" money"
                            if K_r in keys:
                                self.collected = True
                                self.upanimation = True
                                self.pos = vector(self.pos)
                                self.uppos = vector(self.pos)+vector(self.uppos)
                                coins.money -= self.cost
                        else:
                            text = "insufficient funds!"
                            
                        textimage = t.generatetext(text,None,"small",(0,0),(192,192,192))
                        textback = pygame.Surface(textimage.get_size())
                        textback.fill((0,0,0))
                        textback.blit(textimage,(0,0))
                        textrect = textback.get_rect()
                        textrect.centerx = rect.centerx
                        textrect.bottom = player.rect.top+-5
                        screen.blit(textback,textrect)
                else:
                    self.collected = True
                    self.upanimation = True
                    self.pos = vector(self.pos)
                    self.uppos = vector(self.pos)+vector(self.uppos)
            else:
                pass
            if isshop and not self.collected:
                textimage = t.generatetext(str(self.cost)+"£",None,"small",(0,0),(192,192,192))
                textback = pygame.Surface(textimage.get_size())
                textback.fill((0,0,0))
                textback.blit(textimage,(0,0))
                textrect = textback.get_rect()
                textrect.centerx = rect.centerx
                textrect.top = rect.bottom
                screen.blit(textback,textrect)
                

                


spritesheet = pygame.image.load("sprites/coins.png")
coinnum = 0
COINIMAGE = spritesheettolist(spritesheet,2,True)[coinnum]
COINIMAGE_NOOUT = spritesheettolist(spritesheet,2,True,False)[coinnum]

class Coins():
    def __init__(self):
        self.money = 0
        self.coinlist = []
    def addcoins(self,value,pos):
        coinvalue = 5
        evennum = int(value//5)
        oddvalue = value%5
        for _ in range(evennum):
            self.coinlist.append(Coin(pos,coinvalue))
        if oddvalue != 0:
            self.coinlist.append(Coin(pos,oddvalue))
    def update(self,screen,player,entities,inencounter):
        toremove = []
        
        for coin in self.coinlist:
            coin.update(screen,player,entities,inencounter)
            if coin.collected:
                self.money += coin.value
            if coin.delete:
                toremove.append(coin)
                
        for coin in toremove:
            self.coinlist.remove(coin)
    def counter(self,screen,pos):
        textimage = t.generatetext("£"+str(int(self.money)),None,"small",(0,0),(192,192,192))
        textback = pygame.Surface(textimage.get_size())
        textback.fill((0,0,0))
        textback.blit(textimage,(0,0))
        textrect = textback.get_rect()
        textrect.topleft = pos
        screen.blit(textback,textrect)
    
class Coin():
    def __init__(self,pos,value):
        self.slip = uniform(0.04,0.05)
        self.pos = vector(pos)
        self.previousposlist = []
        randomangle = randint(0,360)
        inplace = vector(0,randint(0,10))
        inplace.rotate_ip(randomangle)
        self.spawnpos = self.pos+inplace
        for _ in range(4):
            self.previousposlist.append(self.pos)
        self.collected = False
        self.delete = False
        self.value = value
        self.cango = False
        
    def update(self,screen,player,entities,inencounter):
        if not inencounter and self.cango:
            location = player.pos
            self.pos = vector(self.pos).slerp(location,self.slip)
        else:
            location = self.spawnpos
            self.pos = vector(self.pos).slerp(location,0.5)
        
            
        
        
        self.previousposlist.append(self.pos)
        self.previousposlist.pop(0)

        pygame.draw.lines(screen,(90,90,90),False,self.previousposlist,2)
        imagerect = COINIMAGE_NOOUT.get_rect()
        imagerect.center = self.pos
        screen.blit(COINIMAGE_NOOUT,imagerect)

        glitterprob = uniform(0,1)
        if glitterprob < 0.01:
            randomangle = randint(0,360)
            inplace = vector(0,randint(0,3))
            inplace.rotate_ip(randomangle)
            glitterpos = self.pos+inplace
            length = randint(1,2)
            for angle in range(0,270+1,90):
                entities.add(e.Dust(glitterpos,3,(0,0),angle,length))
        
        if player.rect.collidepoint(self.pos):
            self.delete = True
            self.collected = True
            
        if inttuple(self.pos) == inttuple(self.spawnpos):
            self.cango = True

