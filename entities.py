#this entity module contains code for the Entities, Entity, Enemy, Dust and Projectile classes
import pygame
from pygame.locals import *

import sys,os,time
from random import *
from vector import *
from surfacemethods import *
import room1 as r

#imports the gravity and maximum y velocity constants from the platformer module
from platformer import GRAVITY
from platformer import MAXY



class Entities:
    def __init__(self):
        #create lists to store all the entities in
        self.projectilelist = []
        self.dustlist = []
        self.enemylist = []
        #create types using dummy objects for each type of entity
        #these can be used to detect if an object is an enemy, projectile or dust
        self.enemy = type(Enemy())
        self.projectile = type(Projectile())
        self.dust = type(Dust())

        self.sections = []
        #the screen is square so get the middle of the screen
        halfscreen = r.TILESIZE*(r.TILENUM//2)
        
        #get rects for the screen split up into four quarters, used for collision
        for x in range(2):
            for y in range(2):
                pos = vector(x,y)*halfscreen
                self.sections.append(Rect(pos,(halfscreen,halfscreen)))
                
    
    def updateprojectiles(self,tilelist,player,screen):
        #creates lists containing tiles for every quarter of the screen
        sectlist = [[],[],[],[]]
        for index in range(4):
            section = self.sections[index]
            collisions = section.collidelistall(tilelist)
            for num in collisions:
                sectlist[index].append(tilelist[num])

        #updates projectiles
        for projectile in self.projectilelist:
            projectile.update(self.sections,sectlist,tilelist,self.enemylist,player,screen,self)

        #if projectile.delete is true, delete the projectile
        for projectile in self.projectilelist:
            try:
                if projectile.delete:
                    self.projectilelist.remove(projectile)

            except:
                projectile.delete = False
                
    def updatedusts(self,screen):
        for dust in self.dustlist:
            dust.update(screen)
            
        for dust in self.dustlist:
            try:
                if dust.delete:
                    self.dustlist.remove(dust)

            except:
                dust.delete = False
                
    def updateenemies(self,tilelist,player,screen,unlocks,coins = None):
        for enemy in self.enemylist:
            enemy.update(tilelist,player,screen,self,unlocks,coins)
            
        for enemy in self.enemylist:
            try:
                if enemy.delete:
                    self.enemylist.remove(enemy)

            except:
                enemy.delete = False
                
    def add(self,obj):
        if self.isenemy(obj)and len(self.projectilelist)<400:
            self.enemylist.append(obj)
        elif self.isdust(obj)and len(self.projectilelist)<400:
            self.dustlist.append(obj)
        elif self.isprojectile(obj)and len(self.projectilelist)<400:
            self.projectilelist.append(obj)
        
    def isenemy(self,obj):
        if type(obj)==self.enemy:
            return True
        return False
    def isdust(self,obj):
        if type(obj)==self.dust:
            return True
        return False
    def isprojectile(self,obj):
        if type(obj)==self.projectile:
            return True
        return False

    def update(self,tilelist,player,screen,unlocks,coins=None):
        self.updateenemies(tilelist,player,screen,unlocks,coins)
        self.updateprojectiles(tilelist,player,screen)
        self.updatedusts(screen)
    def clearprojectiles(self,entities):
        for _ in range(5):
            removelist = []
            for projectile in self.projectilelist:
                if not projectile.friendly:
                    projectile.ondeath(entities)
                    removelist.append(projectile)
            for projectile in removelist:
                try:
                    self.projectilelist.remove(projectile)
                except:
                    pass
        
    def clearenemies(self):
        self.enemylist = []
    def cleardust(self):
        self.dustlist = []
    def clearenemyprojectiles(self):
        newlist = []
        for projectile in self.projectilelist:
            if not projectile.friendly:
                projectile.ondeath()

class Entity:
    def __init__(self,pos=(0,0),ident=1,velocity=(0,0),rotation=0,speed=0):
        self.pos = list(pos)
        self.id = ident
        self.velocity = list(velocity)
        self.imagerotation = 0
        self.rotation = rotation
        self.speed = speed
        self.image = pygame.Surface((10,10))
        self.image.fill((200,30,30))
        self.image.convert()
        self.rect = self.image.get_rect()
        self.delete = False
        

    def initid(self):
        pass
    def drawsprite(self,screen):
        self.rect.center = self.pos
        tempimage = self.image.copy()
        imagerect = self.image.get_rect()
        if self.imagerotation != 0:
            tempimage = pygame.transform.rotate(tempimage,self.imagerotation)
            imagerect = self.image.get_rect()
        imagerect.center = self.pos
        screen.blit(tempimage,imagerect)
        
PROJECTILESURFACES = []
PROJECTILESURFACES.append([pygame.image.load("sprites/bullet.png")])
PROJECTILESURFACES.append(spritesheettolist(pygame.image.load("sprites/bubble.png"),4,False,False))
PROJECTILESURFACES.append([pygame.image.load("sprites/clumsyproj.png")])

class Projectile(Entity):
    def __init__(self,pos=(0,0),damage=0,ident=1,velocity=(0,0),rotation=0,speed=0,spectral=False,timetodie=None):
        Entity.__init__(self,pos,ident,velocity,rotation,speed)
        self.damage = damage
        self.pierce = 5
        self.friendly=True
        self.spectral=spectral
        self.hit = []
        
        try:
            self.images = list(PROJECTILESURFACES[ident-1])
        except:
            self.images = []
        
        if self.images != []:
            self.rect = self.images[0].get_rect()
        self.timetodie = None
        if timetodie != None:
            self.timetodie = Timer(timetodie)
        self.initid()
    def initid(self):
        if self.id == 1:
            self.friendly=True
        if self.id == 2:
            self.images2 = list(self.images)
            self.friendly=False
            self.imagetimer = Timer(15)

    def tilecollide(self,entities):
        self.ondeath(entities)
        pass
    def enemycollide(self,enemylist,entities):
        
        for enemy in enemylist:
            self.pierce -=1
            enemy.onhurt(self.damage)
            if self.pierce == 0:
                self.ondeath(entities)
            for x in range(randint(3,5)):
                entities.add(Dust(vector(enemy.pos).lerp(self.pos,0.3),2,(0,0),self.rotation+180+randint(-45,45),randint(3,6)))
        pass
    def playercollide(self,player,entities):
        if self.id == 2:
            self.ondeath(entities)
        player.damage()
    def offscreen(self,screen):
        if False:
            pass
        else:
            self.delete=True
    def ondeath(self,entities):
        self.delete = True
        if self.id == 1:
            for x in range(randint(2,3)):
                entities.add(Dust(self.pos,1,(0,0),self.rotation+180+randint(-50,50),randint(1,3)))
        if self.id == 2:
            for x in range(randint(2,3)):
                entities.add(Dust(self.pos,3,(0,0),randint(0,360),randint(1,3)))
    def normalupdate(self,entities):
        if self.timetodie != None:
            if self.timetodie.update():
                self.ondeath(entities)
        if self.id == 1:
            self.image = self.images[0]
            self.imagerotation = -self.rotation
            if self.speed !=0:
                self.velocity = vector(self.speed,0)
                self.velocity.rotate_ip(self.rotation)
                self.pos = vector(self.pos)+self.velocity
                
        if self.id == 2:
            
            self.image = self.images[0]
            if self.imagetimer.update():
                self.imagetimer.reset()
                self.images.append(self.images.pop(0))
            if self.speed !=0:
                self.velocity = vector(self.speed,0)
                self.velocity.rotate_ip(self.rotation)
                self.pos = vector(self.pos)+self.velocity
        pass

    def update(self,sections,sectlist,tilelist,enemylist,player,screen,entities):
        self.normalupdate(entities)
        self.rect.center = self.pos
        if not self.spectral:
            collisions = self.rect.collidelistall(sections)
            for num in collisions:
                for tile in sectlist[num]:
                    if self.rect.colliderect(tile):
                        self.tilecollide(entities)
                        break
                    
        if self.friendly:
            collidelist = self.rect.collidelistall(enemylist)
            if collidelist !=[]:
                enemycollidelist = []
                for num in collidelist:
                    enemy = enemylist[num]
                    if enemy not in self.hit:
                        self.hit.append(enemy)
                        enemycollidelist.append(enemy)
                    
                self.enemycollide(enemycollidelist,entities)
        else:
            if self.rect.colliderect(player.rect):
                self.playercollide(player,entities)

        if self.rect.top>screen.get_height() or self.rect.bottom<0 or self.rect.left<0 or self.rect.right>screen.get_width():
            self.offscreen(screen)
        if not self.delete:
            self.drawsprite(screen)
        
        

class Dust(Entity):
    def __init__(self,pos=(0,0),ident=1,velocity=(0,0),rotation=0,speed=0):
        Entity.__init__(self,pos,ident,velocity,rotation,speed)
        self.image = pygame.Surface((2,2))
        self.image.fill((100,100,100))
        self.visible = True
        self.initid()
    def initid(self):
        if self.id == 1:
            self.visible = False
            self.colour = (192,192,192)
            self.linesize = 2
            self.slip = 0.05
            self.deletetimer = Timer(randint(6,12))
            
            self.gravity = 0
            
            self.velocity = vector(self.velocity)
            self.traillength = 5
            self.previouslist = []
            for _ in range(self.traillength):
                self.previouslist.append(self.pos)
        if self.id == 2:
            self.visible = False
            self.colour = (90,90,90)
            self.linesize = randint(1,3)
            self.slip = 0.85
            self.deletetimer = Timer(10)

            self.traillength = randint(5,10)
            self.previouslist = []
            for _ in range(self.traillength):
                self.previouslist.append(self.pos)
        if self.id == 3:
            self.visible = False
            self.colour = (192,192,192)
            self.linesize = 1
            self.slip = 0.7
            self.deletetimer = Timer(10)

            self.traillength = 6
            self.previouslist = []
            for _ in range(self.traillength):
                self.previouslist.append(self.pos)
            
            
        pass
    def normalupdate(self,screen):
        if self.id == 1:
            #self.gravity = max(self.gravity+0.02,0.2)
            self.speed = lerp(self.speed,0,0.9)
            #self.velocity  = vector(0,2).lerp(vector(0,2),0.1)
            self.velocity = vector(self.speed,0)
            self.velocity.rotate_ip(self.rotation)
            self.pos = vector(self.pos)+self.velocity+vector(0,self.gravity)
            self.gravity = min(self.gravity+(GRAVITY/5),MAXY)
            
            
            
            self.previouslist.append(self.pos)
            if len(self.previouslist) > self.traillength:
                self.previouslist.pop(0)
            previouspos = self.previouslist[0]
            #pygame.draw.line(screen,self.colour,previouspos,self.pos,self.linesize)
            pygame.draw.lines(screen,self.colour,False,self.previouslist,self.linesize)
            
            if self.deletetimer.update():
                self.colour = (90,90,90)
                self.deletetimer.reset()
                self.traillength -= 2
                self.linesize -=1
                if self.linesize == 0:
                    self.delete = True
        if self.id == 2 or self.id == 3:

            self.velocity = vector(self.speed,0)
            self.velocity.rotate_ip(self.rotation)
            self.pos = vector(self.pos)+self.velocity
            self.speed = lerp(self.speed,0,self.slip)


            self.previouslist.append(self.pos)
            if len(self.previouslist) > self.traillength:
                self.previouslist.pop(0)
            previouspos = self.previouslist[0]
            
            #pygame.draw.line(screen,self.colour,previouspos,self.pos,self.linesize)
            pygame.draw.lines(screen,self.colour,False,self.previouslist,self.linesize)
            if self.speed <= 0.1:
                if self.deletetimer.update():
                    self.deletetimer.reset()
                    self.linesize -= 1
                if self.linesize <= 0:
                    self.delete = True
        
            
        
        pass
    def update(self,screen):
        self.normalupdate(screen)
        if self.visible:
            self.drawsprite(screen)


ENEMYSURFACES = []
ENEMYSURFACES.append(spritesheettolist(pygame.image.load("sprites/froge.png"),2))
ENEMYSURFACES.append(spritesheettolist(pygame.image.load("sprites/mushroom.png"),4,True))
ENEMYSURFACES.append(spritesheettolist(pygame.image.load("sprites/mushroomboss.png"),4))
ENEMYSURFACES.append(spritesheettolist(pygame.image.load("sprites/nosy.png"),1))
ENEMYSURFACES.append(spritesheettolist(pygame.image.load("sprites/clumsy.png"),2))

class Enemy(Entity):
    def __init__(self,pos=(90,90),ident=1,velocity=(0,0),rotation=0,speed=0,difficulty="normal",stagenum = 1):
        Entity.__init__(self,pos,ident,velocity,rotation)
        multipliers = {
            "hard":1.25+(stagenum*0.3),
            "normal":1+(stagenum*0.2),
            "easy":0.75+(stagenum*0.1)
            }
        self.multiplier = multipliers[difficulty]
        #self.speed = 1
        try:
            
            self.images = ENEMYSURFACES[ident-1]
        except:
            self.images = []
        self.hp = 1
        self.contactdamage = 1
        self.shootdamage = 1
        self.sides = {"top":False,
                  "bottom":False,
                  "left":False,
                  "right":False}
        self.initid()
        tilerect = pygame.Rect((0,0),(r.TILESIZE,r.TILESIZE))
        tilerect.topleft = pos
        if self.images == []:
            self.rect = self.image.get_rect()
        else:
            self.rect = self.images[0].get_rect()
        self.rect.center = tilerect.center
        self.rect.bottom = tilerect.bottom
    def initid(self):
        if self.id == 1:
            self.name = "frog"
            self.image = pygame.Surface((30,22))
            self.image.fill((100,100,100))
            self.jumping = False
            self.jumptimer = Timer(60/self.multiplier)
            self.direction = ["left","right"]
            if randint(0,1) == 1:
                self.direction.reverse()
            self.speed = 3
            self.velocity[0] = -self.speed
            self.hp = 10
        if self.id == 2:
            self.name = "mushroom"
            self.velocity[1] = -1
            self.image = pygame.Surface((22,22))
            self.image.fill((100,100,100))
            self.shoottimer = Timer(120/self.multiplier)
            self.direction = ["left","right"]
            if randint(0,1) == 1:
                self.direction.reverse()
            self.speed = 1
            self.velocity[0] = -self.speed
            self.hp = 10
            self.imagetimer = Timer(10)
            self.shootspeed = 2*self.multiplier

        if self.id == 3:
            self.velocity = vector(0,0.0000001)
            self.name = "mushroomboss"
            self.state = "idle"
            self.states = ["idle","attack1","attack2","attack3"]
            self.betweenattackdelay = Timer(200/self.multiplier)
            self.attackdelay = Timer(70/self.multiplier)
            self.bubbledelay = Timer(50/self.multiplier)
            self.bubblespraytime = Timer(10/self.multiplier)
            self.bubblespeed = self.multiplier
            self.attacking = False
            self.shotspeed = 2*self.multiplier
            self.hp = 50
        if self.id == 4:
            self.hp = 20
            self.name = "nosy"
            self.states = ["roam","dash","fall"]
            self.state = "roam"
            self.velocity = vector(0.1,0)
            self.direction = ["left","right"]
            self.speed = 1
            if randint(0,1) == 1:
                self.direction.reverse()
            self.dashdelay = Timer(80/self.multiplier)
            self.hptofall = (self.hp/2)*self.multiplier
            self.ymargin = 10*self.multiplier
        self.hp *= self.multiplier
        self.value = self.hp
    def normalupdate(self,screen,tilelist,entities,player):
        if self.id == 4:
            self.image = self.images[0]
            if self.state == "fall":
                self.velocity[1] = min(self.velocity[1]+GRAVITY,MAXY)
                xdecay = 0.1
                if self.velocity[0] < 0:
                    self.velocity[0] = max(self.velocity[0]+xdecay,0)
                elif self.velocity[0] > 0:
                    self.velocity[0] = min(self.velocity[0]-xdecay,0)
            if self.state == "roam":
                if self.sides["left"] or self.sides["right"]:
                    self.direction.reverse() 
                if self.direction[0] == "left":
                    self.velocity[0] = -self.speed
                else:
                    self.velocity[0] = self.speed
                
                if player.pos[1]> self.pos[1]-self.ymargin and player.pos[1]< self.pos[1]+self.ymargin:
                    xdecay = 0.1
                    if self.direction[0] == "right" and player.pos[0] > self.pos[0]:
                        self.velocity[0] = 0
                        if self.dashdelay.update():
                            self.state = "dash"
                    if self.direction[0] == "left" and player.pos[0] < self.pos[0]:
                        self.velocity[0] = 0
                        if self.dashdelay.update():
                            self.state = "dash"
                else:
                    self.dashdelay.reset()
            if self.state == "dash":
                if self.sides["left"] or self.sides["right"]:
                    self.dashdelay.reset()
                    self.state = "roam"
                if self.direction[0] == "left":
                    self.velocity[0] = -self.speed*3
                else:
                    self.velocity[0] = self.speed*3
                    
            if self.direction[0] == "right":
                self.image = pygame.transform.flip(self.image,True,False)
            
        if self.id == 3:
            self.image = self.images[self.states.index(self.state)]
            if not self.attacking:
                if self.betweenattackdelay.update():
                    self.state = choice(["attack1","attack2","attack3"])
                    self.betweenattackdelay.reset()
                    if self.state == "attack2":
                        self.shots = 3
                    if self.state == "attack1":
                        self.shots = 2
            if self.attacking:
                if self.attackdelay.update():
                    if self.state == "attack1":
                        if self.bubbledelay.update():
                            self.bubbledelay.reset()
                            self.shots -= 1
                            for _ in range(5):
                                vectortoadd = vector(randint(25,125),0)
                                vectortoadd.rotate_ip(randint(0,360))
                                pos = vector(self.pos)+vectortoadd
                                entities.add(Projectile(pos,0,2,(0,0),0,0,True,randint(270,400)))
                            if self.shots == 0:
                                
                                self.state = "idle"
                    if self.state == "attack2":
                        if self.bubbledelay.update():
                            self.bubbledelay.reset()
                            self.shots -= 1
                            playerpos = vector(self.pos)
                            angle = vector(0,0).angle_to(vector(player.pos)-vector(self.pos))
                            entities.add(Projectile(self.pos,0,2,(0,0),angle,self.shotspeed,True))
                            if self.shots == 0:
                                
                                self.state = "idle"
                    if self.state == "attack3":
                        if not self.bubblespraytime.update():
                            for _ in range(2):
                                angle = randint(180+45,360-45)
                                entities.add(Projectile(self.pos,0,2,(0,0),angle,self.shotspeed*uniform(1,0.7)))
                        else:
                            self.state = "idle"
                            self.bubblespraytime.reset()
            if self.state == "idle":
                self.attacking = False
            else:
                self.attacking = True
                            
                        
                        
        if self.id == 1:
            self.velocity[1] = min(self.velocity[1]+GRAVITY,MAXY)
            if self.sides ["top"]:
                self.velocity[1] = 0
            if self.sides["left"] or self.sides["right"]:#self.velocity[0] == 0:
                self.direction.reverse()
                
            if self.sides["bottom"]:
                self.jumping = False
                self.velocity[0] = 0
                if self.jumptimer.update():
                    self.jumptimer.reset()
                    self.velocity[1] = -6
                    self.jumping = True
                    
            if self.jumping:
                self.image = self.images[1]
                if self.direction[0] == "left":
                    
                    self.velocity[0] = -self.speed
                else:
                    self.velocity[0] = self.speed
            else:
                self.image = self.images[0]
            if self.direction[0] == "left":
                self.image = pygame.transform.flip(self.image,True,False)
        if self.id ==2:
            self.image = self.images[0]
            if self.imagetimer.update():
                self.imagetimer.reset()
                self.images.append(self.images.pop(0))
            if self.sides["left"] or self.sides["right"]:#self.velocity[0] == 0:
                self.direction.reverse()
            if self.direction[0] == "left":
                self.velocity[0] = -self.speed
            else:
                self.velocity[0] = self.speed
                
            if self.shoottimer.update():
                self.shoottimer.reset()
                entities.add(Projectile(self.pos,0,2,(0,0),45,self.shootspeed))
                entities.add(Projectile(self.pos,0,2,(0,0),45+90,self.shootspeed))
        if not screen.get_rect().colliderect(self.rect):
            self.pos = (90,90)
            
                
    def onhurt(self,damage):
        if self.id == 4 and self.hp<=self.hptofall:
            self.state = "fall"
        self.hp -= damage
    def playercollide(self,player,unlocks):
        
        if player.damage():
            unlocks.progressachievement(2)
    
    def moveofftile(self,tilelist):
        self.pos = list(self.pos)
        self.pos[1] += self.velocity[1]
        self.rect.center = self.pos
        
        self.sides = {"top":False,
                  "bottom":False,
                  "left":False,
                  "right":False}

        collisions = self.rect.collidelistall(tilelist)
        if collisions!=[]:
            for num in collisions:
                tilerect = tilelist[num].rect
                if self.velocity[1]<0:
                    self.velocity[1] = 0
                    self.rect.top = tilerect.bottom
                    self.sides["top"] = True
                elif self.velocity[1]>0:
                    self.velocity[1] = 0
                    self.rect.bottom = tilerect.top
                    self.sides["bottom"] = True
        
        self.rect.center += vector(self.velocity[0],0)
        
        collisions = self.rect.collidelistall(tilelist)
        if collisions!=[]:
            self.colliding=True
            for num in collisions:
                tilerect = tilelist[num].rect
                if self.velocity[0]<0:
                    self.velocity[0] = 0
                    self.rect.left = tilerect.right
                    self.sides["left"] = True
                elif self.velocity[0]>0:
                    self.velocity[0] = 0
                    self.rect.right = tilerect.left
                    self.sides["right"] = True
        
        self.pos = self.rect.center
    def ondeath(self,unlocks,coins):
        if self.id == 1:
            unlocks.progressachievement(0)
        if coins != None:
            coins.addcoins(self.value,self.pos)
        unlocks.progressachievement(1)
        self.delete = True
    def update(self,tilelist,player,screen,entities,unlocks,coins=None):
        if self.hp <=0:
            self.ondeath(unlocks,coins)
        self.normalupdate(screen,tilelist,entities,player)
        self.rect.center = self.pos
        if self.rect.colliderect(player.rect):
            self.playercollide(player,unlocks)

        self.moveofftile(tilelist)
                
        if not self.delete:
            self.drawsprite(screen)
        
entities = Entities()

                    
