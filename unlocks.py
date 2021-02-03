import pygame
from pygame.locals import *
import sys,os
from random import *

import pickle
import items
from text import *

#The Unlocks object needs all the item images, but these images can be imported from the items module
UNLOCKFILE = "unlocks.dat"
LOCKIMAGE = pygame.image.load("sprites/locked.png")

class Unlocks:
    def __init__(self):
        #list of all the unlocks, the id of each unlock is its place in the list
        self.unlocks = [
            {"description":"kill 20 frogs","progress":0,"condition":20,"finished":False,"item":4},
            {"description":"kill 100 enemies","progress":0,"condition":100,"finished":False,"item":7},
            {"description":"walk into enemies 20 times","progress":0,"condition":50,"finished":False,"item":5},
            {"description":"reach stage 2","progress":False,"condition":True,"finished":False,"item":8},
            ]
        self.getsave()

    #retrieves data from the save file
    def getsave(self):
        if os.path.exists(UNLOCKFILE):
            file = open(UNLOCKFILE,"rb")
            self.unlocks = pickle.load(file)
        else:
            self.writesave()
    #writes data onto the save file
    def writesave(self):
        file = open(UNLOCKFILE,"wb")
        pickle.dump(self.unlocks,file)
        file.close()
    #gets a list of the item ids that the player hasn't unlocked yet
    def getommitteditems(self):
        rejected = []
        for achievement in self.unlocks:
            if not achievement["finished"]:
                rejected.append(achievement["item"])
        return rejected
    
    #when called,moves the achivement at the index one step forward to completion
    def progressachievement(self,achievementindex):
        if achievementindex <= len(self.unlocks):
            achievement = self.unlocks[achievementindex]
            if not achievement["finished"]:
                #if the achievement has a boolean complete condition, set it to true
                if type(achievement["progress"]) == type(True):
                    self.unlocks[achievementindex]["progress"] = True
                #if the achievement has a counter complete condition add 1 to the counter
                if type(achievement["progress"]) == type(int(1)):
                    self.unlocks[achievementindex]["progress"] += 1
                #if the condition is equal to the unlock's progress, mark it as complete
                if self.unlocks[achievementindex]["progress"] == self.unlocks[achievementindex]["condition"]:
                    self.unlocks[achievementindex]["finished"] = True

    #draws text in the menu for unlocks
    #when the mouse hovers over the text, display the item and it's name if it's unlock has been completed
    def drawunlocks(self,screen,mousepos):
        ypointer = 82
        ychange = 12

        #used to store the images and their positions for when the mouse hovers over text
        popupblit = []
        
        for unlock in self.unlocks:
            #the text of the unlock is it's actual description, then a counter if that unlock is countable
            string = unlock["description"]
            if type(unlock["progress"]) == type(1):
                string += "("+str(unlock["progress"])+"/"+str(unlock["condition"])+")"

            #dull the colour and strikethrough the unlock if it has been completed
            if unlock["finished"]:
                colour = (80,80,80)
                text = generatetext(string,None,"small",(0,0),colour)
                pygame.draw.line(text,colour,(0,3),(text.get_width()-2,3))
            else:
                text = generatetext(string,None,"small",(0,0),(192,192,192))

            #draw the text to the screen in the center
            textrect = text.get_rect()
            textrect.centerx = screen.get_width()//2
            textrect.y = ypointer
            screen.blit(text,textrect)
            ypointer += ychange

            #if the mouse touches the text
            if textrect.collidepoint(mousepos):
                #change the image and text if the item is unlocked or not
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

                #put black backgrounds to the images
                back = pygame.Surface(nameimage.get_size())
                back.blit(nameimage,(0,0))
                nameimage = back
                
                back = pygame.Surface(itemimage.get_size())
                back.blit(itemimage,(0,0))
                itemimage = back
                
                popupblit = [[nameimage,namerect],[itemimage,itemrect]]
        #draw the item image and text if it exists
        for image in popupblit:
            screen.blit(image[0],image[1])
    
