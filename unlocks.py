import pygame
from pygame.locals import *
import sys,os
from random import *

import pickle
import items

UNLOCKFILE = "unlocks.dat"

class Unlocks:
    def __init__(self):
        self.unlocks = [
            {"description":"kill 20 frogs","progress":0,"condition":20,"finished":False,"item":4},
            {"description":"kill 100 enemies","progress":0,"condition":100,"finished":False,"item":7},
            {"description":"get hit 50 times","progress":0,"condition":50,"finished":False,"item":5},
            {"description":"reach stage 1","progress":False,"condition":True,"finished":False,"item":4},
            ]
        self.getsave()
    def getsave(self):
        if os.path.exists(UNLOCKFILE):
            file = open(PICKLEFILE,"rb")
            self.unlocks = pickle.load(file)
        else:
            self.writesave()
    def writesave(self):
        file = open(UNLOCKFILE,"wb")
        pickle.dump(self.unlocks,file)
        file.close()
    def getommiteditems(self):
        rejected = []
        for achievement in self.unlocks:
            if not achievement["finished"]:
                rejected.append(achievement["item"])
    def progressachievement(self,achievementindex):
        if achievementindex <= len(self.unlocks):
            achievement = self.unlocks[achievementindex]
            if not achievement["finished"]:
                if type(achievement["progress"]) == type(True):
                    self.unlocks[achievementindex]["progress"] = True
                if type(achievement["progress"]) == type(int(1)):
                    self.unlocks[achievementindex]["progress"] += 1
                if type(self.unlocks[achievementindex]["progress"]) == type(self.unlocks[achievementindex]["condition"]):
                    self.unlocks[achievementindex]["finished"] = True

