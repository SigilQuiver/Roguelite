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


#class that stores entities in lists
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

        #delete all projectiles where projectile.delete=True
        for projectile in self.projectilelist:
            try:
                if projectile.delete:
                    self.projectilelist.remove(projectile)

            except:
                projectile.delete = False
    
    def updatedusts(self,screen):
        #update dusts
        for dust in self.dustlist:
            dust.update(screen)

        #delete all dusts where dust.delete=True
        for dust in self.dustlist:
            try:
                if dust.delete:
                    self.dustlist.remove(dust)

            except:
                dust.delete = False
        
    def updateenemies(self,tilelist,player,screen,unlocks,coins = None):
        #update enemies
        for enemy in self.enemylist:
            enemy.update(tilelist,player,screen,self,unlocks,coins)

        #delete all enemies where enemy.delete=True       
        for enemy in self.enemylist:
            try:
                if enemy.delete:
                    self.enemylist.remove(enemy)

            except:
                enemy.delete = False
    #allows an enemy,dust or projectile object to be added to it's appropriate list
    def add(self,obj):
        #for each type of entity, there can only be max 400
        #determines if the object parameter is an enemy, dust or projectile, then adds it to that list
        if self.isenemy(obj)and len(self.projectilelist)<400:
            self.enemylist.append(obj)
        elif self.isdust(obj)and len(self.projectilelist)<400:
            self.dustlist.append(obj)
        elif self.isprojectile(obj)and len(self.projectilelist)<400:
            self.projectilelist.append(obj)

    #returns true if the object is an enemy
    def isenemy(self,obj):
        if type(obj)==self.enemy:
            return True
        return False
    #returns true if the object is a dust
    def isdust(self,obj):
        if type(obj)==self.dust:
            return True
        return False
    #returns true if the object is a projectile
    def isprojectile(self,obj):
        if type(obj)==self.projectile:
            return True
        return False
    #update all types of entity at once rather than separately
    def update(self,tilelist,player,screen,unlocks,coins=None):
        self.updateenemies(tilelist,player,screen,unlocks,coins)
        self.updateprojectiles(tilelist,player,screen)
        self.updatedusts(screen)
    #clears all projectiles on screen
    def clearprojectiles(self,entities):
        #deletes all enemy projectiles
        #some projectiles have on death effects, the for loop is to make sure if a projectile has an
        #on death that spawns more projectiles, those extra projectiles are deleted too
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
    def clearenemies(self,unlocks=None,coins=None):
        if unlocks == None:
            self.enemylist = []
        else:
            for enemy in self.enemylist:
                enemy.ondeath(unlocks,coins)
    def cleardust(self):
        self.dustlist = []
                
#class inherited by the projectile, enemy and dust classes
class Entity:
    def __init__(self,pos=(0,0),ident=1,velocity=(0,0),rotation=0,speed=0):
        #initialize default attributes for all types of entity
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

    #draws an image based on self.image
    def drawsprite(self,screen):
        #if the image is rotated, make sure that the image is centered (as it's dimensions increases with rotation)
        self.rect.center = self.pos
        tempimage = self.image.copy()
        imagerect = self.image.get_rect()
        if self.imagerotation != 0:
            tempimage = pygame.transform.rotate(tempimage,self.imagerotation)
            imagerect = self.image.get_rect()
        imagerect.center = self.pos
        screen.blit(tempimage,imagerect)

#load constant storing projectile images
PROJECTILESURFACES = []
PROJECTILESURFACES.append([pygame.image.load("sprites/bullet.png")])
#"bubble" is animated, it's image is a spritesheet and the function turns that spritesheet into a list
PROJECTILESURFACES.append(spritesheettolist(pygame.image.load("sprites/bubble.png"),4,False,False))
PROJECTILESURFACES.append([pygame.image.load("sprites/clumsyproj.png")])

class Projectile(Entity):
    #optional parameters when creating a projectile that may need to be changed between projectiles of the same id
    def __init__(self,pos=(0,0),damage=0,ident=1,velocity=(0,0),rotation=0,speed=0,spectral=False,timetodie=None):
        Entity.__init__(self,pos,ident,velocity,rotation,speed)
        self.damage = damage
        self.pierce = 3#pierce is the amount of times a friendly bullet can hit an an enemy
        self.friendly=True
        self.spectral=spectral
        self.hit = []
        
        #the images in the constant PROJECTILESURFACES is in an order such that each index in the list corresponds to it's id (minus one)
        try:
            self.images = list(PROJECTILESURFACES[ident-1])
        except:
            self.images = []
        
        if self.images != []:
            self.rect = self.images[0].get_rect()
            
        #set a death timer if specified
        self.timetodie = None
        if timetodie != None:
            self.timetodie = Timer(timetodie)

        #call initialization for separate ids
        self.initid()
        
    def initid(self):
        #friendly bullet(that the player shoots)
        if self.id == 1:
            self.friendly=True
        #enemy bullet(a bubble)
        if self.id == 2:
            self.images2 = list(self.images)
            self.friendly=False
            self.imagetimer = Timer(15)

    #if the projectile hits a tile
    def tilecollide(self,entities):
        self.ondeath(entities)
        pass
    #if the projectile hits an enemy, can only be called by projectiles with friendly=True
    def enemycollide(self,enemylist,entities):
        for enemy in enemylist:
            #hurt the enemy equal to the projectile's damage
            enemy.onhurt(self.damage)
            #negate the number of times more enemies can be hit by the same projectile
            self.pierce -=1
            if self.pierce == 0:
                self.ondeath(entities)
            #create blood effects when hitting an enemy
            for _ in range(randint(3,5)):
                entities.add(Dust(vector(enemy.pos).lerp(self.pos,0.3),2,(0,0),self.rotation+180+randint(-45,45),randint(3,6)))
    #if the projectile hits the player, can only be called by projectiles with friendly=True
    def playercollide(self,player,entities):
        #enemy bubble
        if self.id == 2:
            #if the bubble hits the player, delete it 
            self.ondeath(entities)
        player.damage()

    #if a projectile manages to get offscreen, delete it
    def offscreen(self,screen):
        self.delete=True
    #called when a projectile is about to be deleted
    def ondeath(self,entities):
        self.delete = True
        
        #friendly bullet
        if self.id == 1:
            #create spark effects
            for x in range(randint(2,3)):
                entities.add(Dust(self.pos,1,(0,0),self.rotation+180+randint(-50,50),randint(1,3)))
                
        #enemy bubble
        if self.id == 2:
            #create pop effects
            for x in range(randint(2,3)):
                entities.add(Dust(self.pos,3,(0,0),randint(0,360),randint(1,3)))

    #the normal behaviour of a projectile,excluding collisions
    def normalupdate(self,entities):
        #if timetodie was specified during initialization, kill the projectile when the frame timer hits 0
        if self.timetodie != None:
            if self.timetodie.update():
                self.ondeath(entities)

        #friendly bullet
        if self.id == 1:
            #self.image = bullet image
            self.image = self.images[0]
            #when the image is drawn it'll face in the direction it's travelling
            self.imagerotation = -self.rotation
            if self.speed !=0:
                #move using it's constant velocity, change it's position
                self.velocity = vector(self.speed,0)
                self.velocity.rotate_ip(self.rotation)
                self.pos = vector(self.pos)+self.velocity

        #enemy bubble
        if self.id == 2:
            #loops the animation for the bubble bouncing
            self.image = self.images[0]
            #when the timer is up, reset it and cycle the list of images
            if self.imagetimer.update():
                self.imagetimer.reset()
                self.images.append(self.images.pop(0))
            #unless it's stationary, update it's position based on velocity
            if self.speed !=0:
                self.velocity = vector(self.speed,0)
                self.velocity.rotate_ip(self.rotation)
                self.pos = vector(self.pos)+self.velocity
        pass

    #called to update the whole projectile
    def update(self,sections,sectlist,tilelist,enemylist,player,screen,entities):
        self.normalupdate(entities)
        self.rect.center = self.pos
        #if a projectile is spectral it can pass through tiles
        if not self.spectral:
            #the areas for collisions are split up into 4 areas of the screen
            #check which of the 4 areas tha projectile is in
            collisions = self.rect.collidelistall(sections)

            #checks collisions with tiles for each area the projectile is in
            for num in collisions:
                for tile in sectlist[num]:
                    if self.rect.colliderect(tile):
                        #call the tile collide method upon a tile collision
                        self.tilecollide(entities)
                        break
        
        #if a projectile can hit enemies
        if self.friendly:
            #check for collisions with all enemies on screen
            collidelist = self.rect.collidelistall(enemylist)
            #if any enemies have collided
            if collidelist !=[]:
                enemycollidelist = []
                for num in collidelist:
                    enemy = enemylist[num]
                    #a list stores enemies already hit so that a projectile can only hit each enemy once
                    if enemy not in self.hit:
                        self.hit.append(enemy)
                        #add enemy to the list, will be passed onto enemycollide to do damage
                        enemycollidelist.append(enemy)
                                    
                self.enemycollide(enemycollidelist,entities)
        #if a projectile can hit the player
        else:
            if self.rect.colliderect(player.rect):
                self.playercollide(player,entities)

        if self.rect.top>screen.get_height() or self.rect.bottom<0 or self.rect.left<0 or self.rect.right>screen.get_width():
            self.offscreen(screen)

        #draw the projectile if it's not been deleted
        if not self.delete:
            self.drawsprite(screen)
        
        

class Dust(Entity):
    def __init__(self,pos=(0,0),ident=1,velocity=(0,0),rotation=0,speed=0):
        Entity.__init__(self,pos,ident,velocity,rotation,speed)
        self.image = pygame.Surface((2,2))
        self.image.fill((100,100,100))
        self.visible = True

        #call initialization for separate ids
        self.initid()
    def initid(self):
        #spark effect - used by player bullets
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
        #blood effect - used when an enemy is hit
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
        #popping effect - used for item collection, coin shine and bubbles popping
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
        #sparks
        if self.id == 1:
            #decrease it's speed as it travels
            self.speed = lerp(self.speed,0,0.9)
            self.velocity = vector(self.speed,0)
            self.velocity.rotate_ip(self.rotation)
            
            #apply gravity acceleration
            self.pos = vector(self.pos)+self.velocity+vector(0,self.gravity)
            self.gravity = min(self.gravity+(GRAVITY/5),MAXY)
            
            
            #add positions onto a list, limit the size of that list based on "traillength"
            self.previouslist.append(self.pos)
            if len(self.previouslist) > self.traillength:
                self.previouslist.pop(0)
            previouspos = self.previouslist[0]
            
            #draw a line from previous positions, creating a trail
            pygame.draw.lines(screen,self.colour,False,self.previouslist,self.linesize)

            #after the timer ends, decrease it's size and make it's colour darker
            if self.deletetimer.update():
                self.colour = (90,90,90)
                self.deletetimer.reset()
                self.traillength -= 2
                self.linesize -=1
                if self.linesize == 0:
                    self.delete = True
                    
        if self.id == 2 or self.id == 3:
            #decrease it's speed as it travels
            self.velocity = vector(self.speed,0)
            self.velocity.rotate_ip(self.rotation)
            self.pos = vector(self.pos)+self.velocity
            self.speed = lerp(self.speed,0,self.slip)

            #add positions onto a list, limit the size of that list based on "traillength"
            self.previouslist.append(self.pos)
            if len(self.previouslist) > self.traillength:
                self.previouslist.pop(0)
            previouspos = self.previouslist[0]
            
            #draw a line from previous positions, creating a trail
            pygame.draw.lines(screen,self.colour,False,self.previouslist,self.linesize)

            #if the dust is stationary
            if self.speed <= 0.1:
                #decrease it's size every time the timer is finished
                if self.deletetimer.update():
                    self.deletetimer.reset()
                    self.linesize -= 1
                if self.linesize <= 0:
                    self.delete = True
                    
    def update(self,screen):
        self.normalupdate(screen)
        if self.visible:
            self.drawsprite(screen)

#add lists of images from spritesheets, each image is given a black outline
ENEMYSURFACES = []
ENEMYSURFACES.append(spritesheettolist(pygame.image.load("sprites/froge.png"),2))
ENEMYSURFACES.append(spritesheettolist(pygame.image.load("sprites/mushroom.png"),4,True))
ENEMYSURFACES.append(spritesheettolist(pygame.image.load("sprites/mushroomboss.png"),4))
ENEMYSURFACES.append(spritesheettolist(pygame.image.load("sprites/nosy.png"),1))
ENEMYSURFACES.append(spritesheettolist(pygame.image.load("sprites/clumsy.png"),2))

class Enemy(Entity):
    def __init__(self,pos=(90,90),ident=1,velocity=(0,0),rotation=0,speed=0,difficulty="normal",stagenum = 1):
        Entity.__init__(self,pos,ident,velocity,rotation)
        #work out difficulty multiplier for the enemy's stats
        multipliers = {
            "hard":1.25+(stagenum*0.3),
            "normal":1+(stagenum*0.2),
            "easy":0.75+(stagenum*0.1)
            }
        self.multiplier = multipliers[difficulty]
        #images are again in the same order as the ids for each enemy
        try:
            self.images = ENEMYSURFACES[ident-1]
        except:
            self.images = []
            
        #create default stats
        self.hp = 1
        self.contactdamage = 1
        self.shootdamage = 1
        self.sides = {"top":False,
                  "bottom":False,
                  "left":False,
                  "right":False}

        #call initialization for separate ids
        self.initid()

        #when an enemy spawns, center it's position on the tile it spawned on
        tilerect = pygame.Rect((0,0),(r.TILESIZE,r.TILESIZE))
        tilerect.topleft = pos
        if self.images == []:
            self.rect = self.image.get_rect()
        else:
            self.rect = self.images[0].get_rect()
        self.rect.center = tilerect.center
        self.rect.bottom = tilerect.bottom
    def initid(self):
        #stats unique to each id are modified by the multiplier individually, unlike health 
        #frog enemy
        if self.id == 1:
            self.name = "frog"
            self.jumping = False
            self.jumptimer = Timer(60/self.multiplier)
            #set a random direction on spawn
            self.direction = ["left","right"]
            if randint(0,1) == 1:
                self.direction.reverse()
            self.speed = 3
            self.velocity[0] = -self.speed
            self.hp = 10
        #mushroom
        if self.id == 2:
            self.name = "mushroom"
            self.velocity[1] = -1
            self.shoottimer = Timer(120/self.multiplier)
            #set a random direction on spawn
            self.direction = ["left","right"]
            if randint(0,1) == 1:
                self.direction.reverse()
            self.speed = 1
            self.velocity[0] = -self.speed
            self.hp = 10
            self.imagetimer = Timer(10)
            self.shotspeed = 2*self.multiplier
        #mushroom boss
        if self.id == 3:
            self.velocity = vector(0,0.0000001)
            self.name = "mushroomboss"
            self.state = "idle"
            self.states = ["idle","attack1","attack2","attack3"]
            self.betweenattackdelay = Timer(200/self.multiplier)
            #the delay upon starting an attack
            self.attackdelay = Timer(70/self.multiplier)
            #the delay between bubbles being shot when firing directly at the player
            self.bubbledelay = Timer(50/self.multiplier)
            #the amount of frames bubbles come out for when firing bubbles upwards
            self.bubblespraytime = Timer(10/self.multiplier)
            self.bubblespeed = self.multiplier
            self.attacking = False
            self.shotspeed = 2*self.multiplier
            self.hp = 50
        """
        #unused skull enemy
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
        """
        self.hp *= self.multiplier
        self.value = self.hp
    def normalupdate(self,screen,tilelist,entities,player):
        #unused skull enemy
        """
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
        """
        #mushroom boss
        if self.id == 3:
            #will change the mushroom's face based on what state it is in
            self.image = self.images[self.states.index(self.state)]
            
            if not self.attacking:
                #once the between attack timer is done, pick a random attack
                if self.betweenattackdelay.update():
                    self.state = choice(["attack1","attack2","attack3"])
                    self.betweenattackdelay.reset()
                    # the amount of times it will repeat an action in a single attack
                    if self.state == "attack2":
                        self.shots = 3
                    if self.state == "attack1":
                        self.shots = 2
                        
            if self.attacking:
                if self.attackdelay.update():
                    #create stationary bubbles around the boss, they can be in walls
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
                    #fire shots directly at the player, can go through walls
                    if self.state == "attack2":
                        if self.bubbledelay.update():
                            self.bubbledelay.reset()
                            self.shots -= 1
                            playerpos = vector(self.pos)
                            angle = vector(0,0).angle_to(vector(player.pos)-vector(self.pos))
                            entities.add(Projectile(self.pos,0,2,(0,0),angle,self.shotspeed,True))
                            if self.shots == 0:
                                self.state = "idle"
                    #spray shots in an upwards cone, can't go through walls
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
                            
                        
        #frog          
        if self.id == 1:
            self.velocity[1] = min(self.velocity[1]+GRAVITY,MAXY)
            #if it hits its head on a wall, decrease it's arc
            if self.sides ["top"]:
                self.velocity[1] = 0
            #if it hits a wall sideways, switch direction
            if self.sides["left"] or self.sides["right"]:
                self.direction.reverse()
            #if it is on the ground, wait for it's jumping timer to end
            if self.sides["bottom"]:
                self.jumping = False
                self.velocity[0] = 0
                if self.jumptimer.update():
                    self.jumptimer.reset()
                    self.velocity[1] = -6
                    self.jumping = True
            #jump forwards in the direction it's facing
            if self.jumping:
                self.image = self.images[1]
                if self.direction[0] == "left":
                    
                    self.velocity[0] = -self.speed
                else:
                    self.velocity[0] = self.speed
            else:
                self.image = self.images[0]
            #flip the image horizontally based on direction
            if self.direction[0] == "left":
                self.image = pygame.transform.flip(self.image,True,False)
        #mushroom
        if self.id ==2:
            #loops an animation
            self.image = self.images[0]
            #once the timer is up, cycle the list
            if self.imagetimer.update():
                self.imagetimer.reset()
                self.images.append(self.images.pop(0))
            #if it hits the side of a wall, change it's direction
            if self.sides["left"] or self.sides["right"]:
                self.direction.reverse()
            if self.direction[0] == "left":
                self.velocity[0] = -self.speed
            else:
                self.velocity[0] = self.speed
                
            #shoot shots diagonally down once a timer is up
            if self.shoottimer.update():
                self.shoottimer.reset()
                entities.add(Projectile(self.pos,0,2,(0,0),45,self.shotspeed))
                entities.add(Projectile(self.pos,0,2,(0,0),45+90,self.shotspeed))
        if not screen.get_rect().colliderect(self.rect):
            self.pos = (90,90)
            
    #lose hp equal to the damage a player did        
    def onhurt(self,damage):
        """
        if self.id == 4 and self.hp<=self.hptofall:
            self.state = "fall"
        """
        
        self.hp -= damage
        
    #hit the player for 1 damage and progress achievement if they walk into the enemy
    def playercollide(self,player,unlocks):
        damaged = player.damage()
        if damaged:
            unlocks.progressachievement(2)

    #tile collision for enemies
    def moveofftile(self,tilelist):
        self.pos = list(self.pos)
        self.pos[1] += self.velocity[1]
        self.rect.center = self.pos

        #list that stores where tiles collided with the enemy
        self.sides = {"top":False,
                  "bottom":False,
                  "left":False,
                  "right":False}

        #apply y velocity, if the enemy collides with a tile, change it's position based on the tile
        
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

        #apply x velocity, if the enemy collides with a tile, change it's position based on the tile
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
        
    #progress achievements and spawn coins when an enemy dies
    def ondeath(self,unlocks,coins):
        if self.id == 1:
            unlocks.progressachievement(0)
        if coins != None:
            coins.addcoins(self.value,self.pos)
        unlocks.progressachievement(31)
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

                    
