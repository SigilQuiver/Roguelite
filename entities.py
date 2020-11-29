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
    #updates
    def updateprojectiles(self,tilelist,player,screen):
        
        for projectile in self.projectilelist:
            projectile.update(tilelist,self.enemylist,player,screen)
            
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
            enemy.update(tilelist,player,screen)
            
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
        elif self.isprojectile(obj)and len(self.projectilelist)<120:
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
        self.friendly=False
        self.spectral=False
        self.hit = []
    def initid(self):
        if self.id == 1:
            self.friendly=True
            

    def tilecollide(self,collidelist):
        self.delete=True
        pass
    def enemycollide(self,collidelist):
        pass
    def playercollide(self,playerss):
        pass
    def offscreen(self,screen):
        if False:
            pass
        else:
            self.delete=True
            
    def normalupdate(self):
        if self.id == 1:
            if self.speed !=0:
                self.velocity = vector(self.speed,0)
                self.velocity.rotate_ip(self.rotation)
                self.pos = vector(self.pos)+self.velocity
        pass

    def update(self,tilelist,enemylist,player,screen):
        self.normalupdate()
        self.rect.center = self.pos
        if not self.spectral:

            for tile in tilelist:
                if self.rect.colliderect(tile):
                    self.tilecollide(tile.rect)
                    
        if self.friendly:

            collidelist = self.rect.collidelistall(enemylist)
            if collidelist !=[]:
                self.enemycollide(collidelist)
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
    def __init__(self,pos=(90,90),damage=0,ident=1,velocity=(0,0),rotation=0,speed=0):
        Entity.__init__(self,pos,ident,velocity,rotation)
        #self.speed = 1
        self.image = pygame.Surface((30,30))
        self.image.fill((100,100,100))
        self.rect = self.image.get_rect()
        self.contactdamage = 1
        self.shootdamage = 1
        self.flying = False
    def initid(self):
        if self.id == 1:
            self.direction = ["left","right"]
            

    def playercollide(self,player):
        pass
    def tilecollide(self,tilerect):
        if self.id == 1:
            self.moveofftile(tilerect)
            pass
        
    def moveofftile(self,tilerect):
        """
        self.pos = list(self.pos)
        self.pos[0] -= self.velocity[0]
        """
        
        self.rect.center = self.pos
        self.rect.center -= vector(self.velocity[0],0)
        
        if self.rect.colliderect(tilerect):
            if self.velocity[1]<0:
                self.velocity[1] = 0
                self.rect.top = tilerect.bottom
            elif self.velocity[1]>0:
                self.velocity[1] = 0
                self.rect.bottom = tilerect.top
        """
        self.pos = list(self.rect.center)
        self.pos[0] += self.velocity[0]
        self.rect.center = self.pos
        """
        
        self.rect.center += vector(0,self.velocity[1])
        
        if self.rect.colliderect(tilerect):
            if self.velocity[0]<0:
                self.velocity[0] = 0
                self.rect.left = tilerect.right
            elif self.velocity[0]>0:
                self.velocity[0] = 0
                self.rect.right = tilerect.left
        
        self.pos = self.rect.center

    def projectilecollide(self,projectilelist=[]):
        pass
    def attack1(self):
        pass
    def attack2(self):
        pass
    def attack3(self):
        pass
    def attack4(self):
        pass
    
    def normalupdate(self,screen):
        if self.id == 1:
            self.velocity[1] = min(self.velocity[1]+GRAVITY,MAXY)
            self.pos += vector(self.velocity)
            
            
            if False:
                speed = 2
                self.direction.reverse()
                if self.direction[0] == "left":
                    self.velocity[0] = -speed
                else:
                    self.velocity[0] = speed
            self.rect.center = self.pos
            if not screen.get_rect().colliderect(self.rect):
                self.pos = (90,90)
            
            
    def getunitarea(self):
        unittop= self.rect.top // r.TILESIZE
        unitbottom = self.rect.bottom // r.TILESIZE
        unitright = self.rect.right // r.TILESIZE
        unitleft = self.rect.left // r.TILESIZE
        arealist = []
        for x in range(unittop, unitbottom):
            for y in range(unitright,unitleft):
                arealist.append([x,y])

    def getunitlist(self,tilelist):
        unitlist = []
        for tile in tilelist:
            unitlist.append(tile.rect.topleft//r.TILESIZE)
    def update(self,tilelist,player,screen):
        
        self.normalupdate(screen)
        self.rect.center = self.pos
        if self.rect.colliderect(player.rect):
            self.playercollide(player)
            
        self.colliding = False
        for tile in tilelist:
            if self.rect.colliderect(tile.rect):
                #print(tile.rect.center,self.pos,self.velocity)
                self.tilecollide(tile.rect)
                self.colliding = True
                
                
        if not self.delete:
            self.drawsprite(screen)
        
entities = Entities()

                    
