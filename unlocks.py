import pygame
from pygame.locals import *
import sys,os
from random import *

import pickle
import items
from text import *

UNLOCKFILE = "unlocks.dat"
LOCKIMAGE = pygame.image.load("sprites/locked.png")

class Unlocks:
    def __init__(self):
        self.unlocks = [
            {"description":"kill 20 frogs","progress":0,"condition":20,"finished":False,"item":4},
            {"description":"kill 100 enemies","progress":0,"condition":100,"finished":False,"item":7},
            {"description":"walk into enemies 20 times","progress":0,"condition":50,"finished":False,"item":5},
            {"description":"reach stage 2","progress":False,"condition":True,"finished":False,"item":8},
            ]
        self.getsave()
    def getsave(self):
        if os.path.exists(UNLOCKFILE):
            file = open(UNLOCKFILE,"rb")
            self.unlocks = pickle.load(file)
        else:
            self.writesave()
    def writesave(self):
        file = open(UNLOCKFILE,"wb")
        pickle.dump(self.unlocks,file)
        file.close()
    def getommitteditems(self):
        rejected = []
        for achievement in self.unlocks:
            if not achievement["finished"]:
                rejected.append(achievement["item"])
        return rejected
    def progressachievement(self,achievementindex):
        if achievementindex <= len(self.unlocks):
            achievement = self.unlocks[achievementindex]
            if not achievement["finished"]:
                if type(achievement["progress"]) == type(True):
                    self.unlocks[achievementindex]["progress"] = True
                if type(achievement["progress"]) == type(int(1)):
                    self.unlocks[achievementindex]["progress"] += 1
                if self.unlocks[achievementindex]["progress"] == self.unlocks[achievementindex]["condition"]:
                    self.unlocks[achievementindex]["finished"] = True

    def drawunlocks(self,screen,mousepos):
        ypointer = 82
        ychange = 12

        popupblit = []
        for unlock in self.unlocks:
            string = unlock["description"]
            if type(unlock["progress"]) == type(1):
                string += "("+str(unlock["progress"])+"/"+str(unlock["condition"])+")"
            if unlock["finished"]:
                colour = (80,80,80)
                text = generatetext(string,None,"small",(0,0),colour)
                pygame.draw.line(text,colour,(0,3),(text.get_width()-2,3))
            else:
                text = generatetext(string,None,"small",(0,0),(192,192,192))
            
            textrect = text.get_rect()
            textrect.centerx = screen.get_width()//2
            textrect.y = ypointer
            screen.blit(text,textrect)
            ypointer += ychange

            if textrect.collidepoint(mousepos):
                if unlock["finished"]:
                    itemname = items.Item(unlock["item"]).name
                    itemimage = items.SURFACES[str(unlock["item"])]
                else:
                    itemname = "locked"
                    itemimage = LOCKIMAGE
                itemrect = itemimage.get_rect()
                itemrect.topleft = mousepos
            
                nameimage = generatetext(itemname,None,"small",(0,0),(192,192,192))
                namerect = nameimage.get_rect()
                namerect.center = itemrect.center
                namerect.top = itemrect.bottom
                
                back = pygame.Surface(nameimage.get_size())
                back.blit(nameimage,(0,0))
                nameimage = back
                
                back = pygame.Surface(itemimage.get_size())
                back.blit(itemimage,(0,0))
                itemimage = back
                
                popupblit = [[nameimage,namerect],[itemimage,itemrect]]

        for image in popupblit:
            screen.blit(image[0],image[1])
    
