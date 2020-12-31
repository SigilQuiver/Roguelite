import pygame
from pygame.locals import *

import sys
from random import *

from vector import *

from text import *

pygame.init()

screen = pygame.display.set_mode((600,600),pygame.RESIZABLE)

from surfacemethods import *

import configparser
    

class Quickprint:
    def __init__(self):
        self.printlist = []
    def update(self,screen,xpos = None):
        surfacelist = []
        ypointer=0
        for string in self.printlist:
            surface = textgen.generatetext(string)
            surface = changecolour(surface,(0,0,0),(11,180,11))
            back = surface.copy()
            back.fill((0,0,0))
            back.blit(surface,(0,0))
            surface=back
            rect = surface.get_rect()
            rect.y = ypointer
            if xpos == None:
                rect.right = screen.get_width()
            else:
                rect.right = xpos
            screen.blit(surface,rect)
            ypointer += rect.height
        self.printlist = []
    def print(self,*strings):
        string = ""
        for x in strings:
            string += str(x)
        self.printlist.append(string+" ")

quick = Quickprint()

class Button:
    def __init__(self,text,pos,center=False):
        self.center = center
        self.text = text
        self.textcolour = (192,192,192)
        self.textimage = textgen.generatetext(text)
        self.textimage = changecolour(self.textimage,(0,0,0),self.textcolour)
        self.colourhighlight = 50
        self.colournormal = 0
        self.actualcolour = self.colournormal
        self.extendsides = 0
        self.maxextend = 4
        self.buttonsurface = pygame.Surface((vector(self.textimage.get_size())+vector(1,1)))
        self.rect = self.buttonsurface.get_rect()
        self.rect.topleft = pos
        if self.center:
            self.rect.centerx = pos[0]
        self.pressed = False
        self.alreadyclicked = True
        self.toreturn = False
    def update(self,surface,mousepos,screenmiddle=None):

        if screenmiddle != None:
            if self.center:
                self.rect.centerx = screenmiddle
        
        if self.rect.collidepoint(mousepos):
            self.actualcolour = lerp(self.actualcolour,self.colourhighlight,0.9)
        else:
            self.actualcolour = lerp(self.actualcolour,self.colournormal,0.9)

        self.buttonsurface = pygame.Surface((vector(self.textimage.get_size())+vector(1,1)+vector(self.extendsides*2,0)))
        self.buttonsurface.fill((int(self.actualcolour),int(self.actualcolour),int(self.actualcolour)))
        temprect = self.buttonsurface.get_rect()
        temprect.center = self.rect.center
        
        surface.blit(self.buttonsurface,temprect)
        surface.blit(self.textimage,vector(self.rect.topleft)+vector(1,1))
        
        if self.extendsides > 0:
            if self.extendsides < 0.3:
                self.extendsides = 0
            
            self.extendsides = lerp(self.extendsides,0,0.8)
        if self.pressed:
            self.actualcolour = lerp(self.actualcolour,self.textcolour[0],0.8)

        self.toreturn = False
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(mousepos) and not self.alreadyclicked:
            if not self.pressed and not self.alreadyclicked:
                self.extendsides = self.rect.width/self.maxextend
                self.toreturn = True
            self.pressed = True
        if pygame.mouse.get_pressed()[0] and not self.rect.collidepoint(mousepos):
            self.alreadyclicked = True
        if not pygame.mouse.get_pressed()[0]:
            self.alreadyclicked = False
            self.pressed = False
            
        return self.toreturn
        
    
    def changetext(self,text):
        self.textcolour = (192,192,192)
        self.textimage = textgen.generatetext(text)
        self.textimage = changecolour(self.textimage,(0,0,0),self.textcolour)
        pos = self.rect.topleft
        centerx = self.rect.centerx
        self.buttonsurface = pygame.Surface((vector(self.textimage.get_size())+vector(1,1)))
        self.rect = self.buttonsurface.get_rect()
        self.rect.topleft = pos
        if self.center:
            self.rect.centerx = centerx
    def reset(self):
        self.__init__(self.text,self.rect.topleft)

class Toggle:
    def __init__(self,text,types,pos,center=False):
        self.text = text
        self.center = center
        self.types = types
        self.minspaceneeded = 0
        for var in types:
            string = self.text+":"+str(var)
            self.minspaceneeded = max(self.minspaceneeded,len(string))
        self.indent = 0
        self.button = Button(self.getbuttonstring(),pos,self.center)

    def getbuttonstring(self):
        string = self.text+":"+str(self.types[0])
        extraindents = (self.minspaceneeded)-len(string)
        spaces = ""
        for _ in range(self.indent+extraindents):
            spaces += " "
        string = self.text+":"+spaces+str(self.types[0])
        return string

    def cycletypes(self):
        self.types.append(self.types.pop(0))
        self.button.changetext(self.getbuttonstring())
    def update(self,screen,mousepos,screenmiddle=None):
        if self.button.update(screen,mousepos,screenmiddle):
            self.cycletypes()
        return self.types[0]
    def settype(self,toset):
        if toset in self.types:
            while self.types[0] != toset:
                self.cycletypes()

    def returncurrent(self):
        return self.types[0]
    def reset(self):
        self.button.reset()
        
class Menu:
    def __init__(self,screen,screenmiddle=None):
        fullscreenresolutions = []
        for tup in pygame.display.list_modes():
            if tup not in fullscreenresolutions:
                fullscreenresolutions.append(tup)
                
        self.states = {
            "play":{
                "continue":"savedgame",
                "new playthrough":{
                    "difficulty":["toggle",["easy","normal","hard"]],
                    "start new game":"newgame",
                    "back|1":"back"
                    },
                "see unlocks":None,
                "back|2":"back"
                },
            "options":{
                "fullscreen":["toggle",[True,False]],
                "fullscreen resolution":["toggle",fullscreenresolutions],
                "pixel-perfect":["toggle",[True,False]],
                "visual effects cull":["toggle",[True,False]],
                "apply":"apply",
                "back|3":"back"
                },
            "exit":"exit"
            }
        self.widgets = {}
        self.dicttype = type(dict({}))
        self.listtype = type(list([]))
        self.stringtype = type(str(""))
        self.buttontype = type(Button("cringe",(30,30)))
        self.buttonresults = {}
        self.returnwidgets(self.states,screen,screenmiddle)
        self.getfromfile()
        self.currentstates = []
        
        
    def returnwidgets(self,states,screen,screenmiddle=None):
        ypointer = 40
        if screenmiddle == None:
            startingx = screen.get_width()//2
        else:
            startingx = screenmiddle
        for key in states:
            pos = (startingx,ypointer)
            if type(states[key]) == self.dicttype:
                self.returnwidgets(states[key],screen)
                self.widgets[key] = Button(key,pos,True)
            if type(states[key]) == self.listtype:
                if states[key][0] == "toggle":
                    self.widgets[key] = Toggle(key,states[key][1],pos,True)
            if type(states[key]) == self.stringtype or states[key] == None:
                string = key
                if "|" in list(key):
                    while "|" in list(string):
                        string  = string[:-1]
                self.widgets[key] = Button(string,pos,True)
                if string != "back":
                    self.buttonresults[key] = False
            ypointer += 10
            
    def update(self,screen,mousepos,screenmiddle=None):
        state = self.states
        for key in self.currentstates:
            state = state[key]
        
        keys = state.keys()
        for key in keys:
            reaction = self.widgets[key].update(screen,mousepos,screenmiddle)
    
            if type(state[key]) == self.stringtype:
                if state[key] == "back" and reaction:
                    self.writetofile()
                    for key2 in keys:
                        if type(self.widgets[key2]) == self.buttontype:
                            self.widgets[key2].reset()
                    self.currentstates.pop(len(self.currentstates)-1)
                else:
                    self.buttonresults[state[key]] = self.widgets[key].toreturn
                if state[key] == "apply" and reaction:
                    self.writetofile()
                    
            if type(state[key]) == self.dicttype and reaction:
                self.writetofile()
                for key2 in keys:
                    if type(self.widgets[key2]) == self.buttontype:
                            self.widgets[key2].reset()
                self.currentstates.append(key)
                
    def getoptions(self):
        resultdict = {}
        toggletype = type(Toggle("",[True,False],(0,0)))
        for key in self.widgets:
            widget = self.widgets[key]
            if type(widget) == toggletype:
                resultdict[key] = self.widgets[key].returncurrent()
        return resultdict
    def reposition(self,screen,screenmiddle=None):
        currentstates = list(self.currentstates)
        resultdict = self.getoptions()
        self.__init__(screen,screenmiddle)
        self.currentstates = currentstates
        for key in resultdict:
            self.widgets[key].settype(resultdict[key])
    def getbuttonresults(self):
        return self.buttonresults
    def writetofile(self):
        resultdict = self.getoptions()
        config = configparser.ConfigParser()
        config["play"] = {}
        config["options"] = {}
        inplay = ["difficulty"]
        inoptions = ["fullscreen","fullscreen resolution","pixel-perfect","visual effects cull"]
        for key in inplay:
            config["play"][key] = str(resultdict[key])
        for key in inoptions:
            config["options"][key] = str(resultdict[key])
        settings = open('settings.ini', 'w')
        config.write(settings)
        settings.close()
        
    def getfromfile(self,setwidgets = True):
        
        extra = {}
        config = configparser.ConfigParser()
        config.read("settings.ini")
        resultdict = {}
        resultdictsection = {}
        for section in config.sections():
            for key in config[section]:
                value = str(config[section][key])
                if value[0] == "(":
                    num1,num2 = value[1:-1].split(",")
                    value = (int(num1),int(num2))
                if value in ["True","False"]:
                    value = config.getboolean(section,key)
                resultdictsection[key] = section
                resultdict[key] = value
                
        for key in resultdict:
            if key not in self.widgets:
                extra[key] = [resultdict[key],resultdictsection[key]]
            else:
                if setwidgets:
                    self.widgets[key].settype(resultdict[key])
        return extra
        

class Gamemenu(Menu):
    def __init__(self,screen,screenmiddle=None):
        Menu.__init__(self,screen,screenmiddle)
        fullscreenresolutions = []
        for tup in pygame.display.list_modes():
            if tup not in fullscreenresolutions:
                fullscreenresolutions.append(tup)
                
        self.states = {
            "return":"return",
            "see unlocks":None,
            "options":{
                "fullscreen":["toggle",[True,False]],
                "fullscreen resolution":["toggle",fullscreenresolutions],
                "pixel-perfect":["toggle",[True,False]],
                "visual effects cull":["toggle",[True,False]],
                "apply":"apply",
                "back|3":"back"
                },
            "save run":"save",
            "exit to menu":"menu",
            "exit game":"exit"
            }
        self.widgets = {}
        self.returnwidgets(self.states,screen,screenmiddle)
        self.getfromfile()
    def writetofile(self):
        extras = self.getfromfile(False)
        resultdict = self.getoptions()
        config = configparser.ConfigParser()
        config["play"] = {}
        config["options"] = {}
        inplay = []
        for lst in extras:
            section = lst[1]
            result = lst[0]
            if section not in config.keys():
                config[section] = {}
            
        
        inoptions = ["fullscreen","fullscreen resolution","pixel-perfect","visual effects cull"]
        for key in inplay:
            config["play"][key] = str(resultdict[key])
        for key in inoptions:
            config["options"][key] = str(resultdict[key])
        settings = open('settings.ini', 'w')
        for key in extras:
            
            section = extras[key][1]
            result = extras[key][0]
            if section == "play" and result not in inplay:
                config["play"][key] = str(result)
        config.write(settings)
        settings.close()

        

    
                
            
        
"""     
clock = pygame.time.Clock()

btn1 = Button("cringe",(30,30))
btn2 = Button("cringeasdf",(30,40))
btn3 = Button("cringeasdfasdfasdfas",(30,50))
btn4 = Button("cringeasdfasdfasdfasdfasdfa.",(30,60))

toggle1 = Toggle("toggle",["without many spaces","small phrase"],(screen.get_width()//2,40),True)

menu = Menu(screen)
while True:

    for event in pygame.event.get():
        pass
    
    screen.fill((0,0,0))
    clock.tick(90)
    mousepos = vector(pygame.mouse.get_pos())
    menu.update(screen,mousepos)
    #screen.blit(pygame.transform.scale(screen,inttuple(vector(screen.get_size())*2)),(0,0))
    
    pygame.display.flip()
"""
    
