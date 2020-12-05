#this entity module contains code for the Entities, Entity, Enemy, Dust and Projectile classes
import pygame
from pygame.locals import *

import sys,os,time
from random import *
from vector import *
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
        halfscreen = r.TILESIZE*(r.TILENUM//2)
        for x in range(2):
            for y in range(2):
                pos = vector(x,y)*halfscreen
                self.sections.append(Rect(pos,(halfscreen,halfscreen)))
                
    #updates
    def updateprojectiles(self,tilelist,player,screen):
        sectlist = [[],[],[],[]]
        for index in range(4):
            section = self.sections[index]
            
            collisions = section.collidelistall(tilelist)
            for num in collisions:
                sectlist[index].append(tilelist[num])
                
        for projectile in self.projectilelist:
            projectile.update(self.sections,sectlist,tilelist,self.enemylist,player,screen,self)
            
        for projectile in self.projectilelist:
            try:
                if projectile.delete:
                    self.projectilelist.remove(projectile)

            except:
                projectile.delete = False
                
    def updatedusts(self):
        for dust in self.dustlist:
            dust.update()
            
        for dust in self.dustlist:
            try:
                if projectile.delete:
                    self.dustlist.remove(projectile)

            except:
                projectile.delete = False
                
    def updateenemies(self,tilelist,player,screen):
        for enemy in self.enemylist:
            enemy.update(tilelist,player,screen,self)
            
        for enemy in self.enemylist:
            try:
                if enemy.delete:
                    self.enemylist.remove(enemy)

            except:
                enemy.delete = False
                
    def add(self,obj):
        if self.isenemy(obj):
            self.enemylist.append(obj)
        elif self.isdust(obj):
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

    def update(self,tilelist,player,screen):
        self.updateprojectiles(tilelist,player,screen)
        self.updatedusts()
        self.updateenemies(tilelist,player,screen)
    def clearprojectiles(self):
        self.projectilelist = []
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
        
        self.initid()
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
        
        

class Projectile(Entity):
    def __init__(self,pos=(0,0),damage=0,ident=1,velocity=(0,0),rotation=0,speed=0):
        Entity.__init__(self,pos,ident,velocity,rotation,speed)
        self.pierce = 5
        self.friendly=True
        self.spectral=False
        self.hit = []
        self.initid()
    def initid(self):
        if self.id == 1:
            self.friendly=True
            self.damage = 2
        if self.id == 2:
            self.friendly=False
    def tilecollide(self):
        self.ondeath()
        pass
    def enemycollide(self,enemylist):
        
        for enemy in enemylist:
            self.pierce -=1
            enemy.hp -= self.damage
            if self.pierce == 0:
                self.ondeath()
        pass
    def playercollide(self,player):
        player.damage()
    def offscreen(self,screen):
        if False:
            pass
        else:
            self.delete=True
    def ondeath(self):
        self.delete = True
    def normalupdate(self):
        if self.id == 1:
            if self.speed !=0:
                self.velocity = vector(self.speed,0)
                self.velocity.rotate_ip(self.rotation)
                self.pos = vector(self.pos)+self.velocity
        pass

    def update(self,sections,sectlist,tilelist,enemylist,player,screen,entities):
        self.normalupdate()
        self.rect.center = self.pos
        if not self.spectral:
            collisions = self.rect.collidelistall(sections)
            for num in collisions:
                for tile in sectlist[num]:
                    if self.rect.colliderect(tile):
                        self.tilecollide()
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
                    
                self.enemycollide(enemycollidelist)
        else:
            if self.rect.colliderect(player.rect):
                self.playercollide(player)

        if self.rect.top>screen.get_height() or self.rect.bottom<0 or self.rect.left<0 or self.rect.right>screen.get_width():
            self.offscreen(screen)
        if not self.delete:
            self.drawsprite(screen)
        
        

class Dust(Entity):
    def __init__(self,pos=(0,0),ident=1,velocity=(0,0),rotation=0,speed=0):
        Entity.__init__(self,pos,ident,velocity,rotation)
    def initid(self):
        pass
    def normalupdate(self):
        pass
    def update(self):
        self.normalupdate()
        
        
class Enemy(Entity):
    def __init__(self,pos=(90,90),ident=1,velocity=(0,0),rotation=0,speed=0):
        Entity.__init__(self,pos,ident,velocity,rotation)
        #self.speed = 1
        self.hp = 1
        
        self.contactdamage = 1
        self.shootdamage = 1
        self.flying = False
        self.sides = {"top":False,
                  "bottom":False,
                  "left":False,
                  "right":False}
        self.initid()
        tilerect = pygame.Rect((0,0),(r.TILESIZE,r.TILESIZE))
        tilerect.topleft = pos
        self.rect = self.image.get_rect()
        self.rect.center = tilerect.center
    def initid(self):
        if self.id == 1:
            self.image = pygame.Surface((30,22))
            self.image.fill((100,100,100))
            self.jumping = False
            self.jumptimer = Timer(40)
            self.direction = ["left","right"]
            if randint(0,1) == 1:
                self.direction.reverse()
            self.speed = 3
            self.velocity[0] = -self.speed
            self.hp = 10
        if self.id == 2:
            self.image = pygame.Surface((22,22))
            self.image.fill((100,100,100))
            self.shoottimer = Timer(40)
            self.direction = ["left","right"]
            if randint(0,1) == 1:
                self.direction.reverse()
            self.speed = 3
            self.velocity[0] = -self.speed
            self.hp = 10
    def normalupdate(self,screen,tilelist,entities):
        if self.id == 1:
            self.velocity[1] = min(self.velocity[1]+GRAVITY,MAXY)
            if self.sides["left"] or self.sides["right"]:#self.velocity[0] == 0:
                self.direction.reverse()
                
            if self.sides["bottom"]:
                self.jumping = False
                self.velocity[0] = 0
                if self.jumptimer.update():
                    self.jumptimer.reset()
                    self.velocity[1] = -5
                    self.jumping = True
                    
            if self.jumping:
                if self.direction[0] == "left":
                    self.velocity[0] = -self.speed
                else:
                    self.velocity[0] = self.speed
        if self.id ==2:
            if self.sides["left"] or self.sides["right"]:#self.velocity[0] == 0:
                self.direction.reverse()
                
            if self.shoottimer.update():
                self.shoottimer.reset()
                entities.append(Projectile(self.pos,0,2,(0,0),45,2))
                entities.append(Projectile(self.pos,0,2,(0,0),45+90,2))
        if not screen.get_rect().colliderect(self.rect):
            self.pos = (90,90)
            
                
                
    def playercollide(self,player):
        player.damage()
    
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
    def ondeath(self):
        self.delete = True
    def update(self,tilelist,player,screen,entities):
        if self.hp <=0:
            self.ondeath()
        self.normalupdate(screen,tilelist,entities)
        self.rect.center = self.pos
        if self.rect.colliderect(player.rect):
            self.playercollide(player)

        self.moveofftile(tilelist)
                
        if not self.delete:
            self.drawsprite(screen)
        
entities = Entities()

                    
