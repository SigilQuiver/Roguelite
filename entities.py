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

    def update(self,tilelist,player,screen):
        self.updateenemies(tilelist,player,screen)
        self.updateprojectiles(tilelist,player,screen)
        self.updatedusts(screen)
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

class Projectile(Entity):
    def __init__(self,pos=(0,0),damage=0,ident=1,velocity=(0,0),rotation=0,speed=0):
        Entity.__init__(self,pos,ident,velocity,rotation,speed)
        self.damage = damage
        self.pierce = 5
        self.friendly=True
        self.spectral=False
        self.hit = []
        
        try:
            self.images = list(PROJECTILESURFACES[ident-1])
        except:
            self.images = []
        
        if self.images != []:
            self.rect = self.images[0].get_rect()
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
            enemy.hp -= self.damage
            if self.pierce == 0:
                self.ondeath(entities)
            for x in range(randint(3,5)):
                entities.add(Dust(vector(enemy.pos).lerp(self.pos,0.3),2,(0,0),self.rotation+180+randint(-45,45),randint(3,6)))
        pass
    def playercollide(self,player):
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
                self.playercollide(player)

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
            self.linesize = 1
            self.slip = 0.1
            self.deletetimer = Timer(randint(6,12))
            
            self.gravity = 0.1
            
            self.velocity = vector(self.velocity)
            self.traillength = randint(2,3)
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
            
            self.velocity  = self.velocity.lerp(vector(0,2),0.1)
            self.velocity = vector(self.speed,0)
            self.velocity.rotate_ip(self.rotation)
            self.pos = vector(self.pos)+self.velocity
            
            
            self.previouslist.append(self.pos)
            if len(self.previouslist) > self.traillength:
                self.previouslist.pop(0)
            previouspos = self.previouslist[0]
            #pygame.draw.line(screen,self.colour,previouspos,self.pos,self.linesize)
            pygame.draw.lines(screen,self.colour,False,self.previouslist,self.linesize)

            if self.deletetimer.update():
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

class Enemy(Entity):
    def __init__(self,pos=(90,90),ident=1,velocity=(0,0),rotation=0,speed=0):
        Entity.__init__(self,pos,ident,velocity,rotation)
        #self.speed = 1
        try:
            
            self.images = ENEMYSURFACES[ident-1]
        except:
            self.images = []
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
        if self.images == []:
            self.rect = self.image.get_rect()
        else:
            self.rect = self.images[0].get_rect()
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
            self.velocity[1] = -1
            self.image = pygame.Surface((22,22))
            self.image.fill((100,100,100))
            self.shoottimer = Timer(120)
            self.direction = ["left","right"]
            if randint(0,1) == 1:
                self.direction.reverse()
            self.speed = 1
            self.velocity[0] = -self.speed
            self.hp = 10
            self.imagetimer = Timer(10)
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
                entities.add(Projectile(self.pos,0,2,(0,0),45,2))
                entities.add(Projectile(self.pos,0,2,(0,0),45+90,2))
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

                    
