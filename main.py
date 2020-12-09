    #this is the main script for the game, which uses all the other modules
import pygame
from pygame.locals import *

import time
from datetime import datetime
import sys
from random import *

import map1 as m
import room1 as r
import entities as e
import platformer

from menu import *
from vector import *



import pickle

#the file to which a current playthrough will be saved to
PICKLEFILE = "run.dat"

#initialize pygame
pygame.init()

#the screenlength is the size of the screen where the player will be
screenlength = r.TILESIZE*r.TILENUM
#creates dimensions for the square screen that will be used for the game
gamesize = (screenlength,screenlength)
#variable used to toggle fullscreen
fullscreen = True
#pixel perfect determines if the screen stretches to fit the screen (often resulting in stretched pixels)
#or if the screen is placed in the middle of the screen so that each pixel is a perfect square
pixelperfect = True

#creates a pygame screen object, some other modules have already done this, but this overrides all of the existing screens in those modules
screen = pygame.display.set_mode((screenlength,screenlength),pygame.RESIZABLE)
#gets the dimensions for the current display size
fullscreensize = pygame.display.list_modes()[0]
#creates a background to be drawn on top of other sprites every frame
background = pygame.Surface(screen.get_rect().size)


#adds borders to a tuple representation of a room, leaving holes where the player can move to different rooms
#the gaps will changed based on which direction the room is coming from
def processroom(room,directions):
    #get the furthest grid coordinates at the edge of the screen
    last = r.TILENUM-1
    roomtemp = []
    for tile in room:
        #tile contains a list of both the coordinates (as a list) and the tile id of that tile, i only want the coordinates to be in roomtemp
        roomtemp.append(tuple(tile[1]))

    #creates a border around the whole room
    for x in range(0,last+1,last):
        for y in range(last+1):
            if (x,y) not in roomtemp:
                roomtemp.append((x,y))
    for y in range(0,last+1,last):
        for x in range(last+1):
            if (x,y) not in roomtemp:
                roomtemp.append((x,y))
    #get the middle position of the square game screen in units(for the grid of tiles)
    median = r.TILENUM//2
    median -= 1

    #the directions passed into this function are used to make holes in the border
    #the tiles to be deleted are added to a list
    rejected = []
    for direction in directions:
        coords = None
        if direction == "w":
            for x in range(-1,3):
                coords = (0,median+x)
                rejected.append(coords)
        
        if direction == "e":
            for x in range(-1,3):
                coords = (last,median+x)
                rejected.append(coords)
        
        if direction == "n":
            for x in range(-1,3):
                coords = (median+x,0)
                rejected.append(coords)
        if direction == "s":
            for x in range(-1,3):
                coords = (median+x,last)
                rejected.append(coords)
    #adds all tiles except the ones in the list "rejected" to a new list
    newroom = []
    for coords in roomtemp:
        if coords not in rejected:
            newroom.append([1,coords])

    #returns a list of unit coordinate positions
    return newroom

#returns a dictionary showing which nodes special rooms should be assigned to
def assignspecialrooms(tree):
    #set up dictionary for the top 3 amount of rooms from the center
    roomtop3 = {"1":["a",0],
                "2":["b",0],
                "3":["c",0]}
    #get the dead ends from the tree
    deadends,notdeadends = m.getdeadends(tree)
    #put the nodes for the top 3 amount of rooms into the dictionary
    for key in deadends:
        magnitude = len(m.getdirections(key,tree,1))
        #for each place in dictionary
        for place in roomtop3:
            #if the amount of rooms is bigger than what is already in the dictionary
            if magnitude > roomtop3[place][1] and key in deadends:
                #move existing places up and down if something needs to be placed ahead
                if place == "1" or place == "2":
                    roomtop3["3"] = roomtop3["2"]
                if place == "1":
                    roomtop3["2"] = roomtop3["1"]
                roomtop3[place] = [key,magnitude]
                break
    #assign the most rooms to boss, second most to shop and the third most to item
    specialrooms = ["boss","shop","item"]
    specialdict = {}
    for key in roomtop3:
        keytochange = roomtop3[key][0]
        specialdict[keytochange] = specialrooms.pop(0)
    return specialdict

#returns a dictionary with room objects for each node in the tree
def treestorooms(tree):
    roomdict = {}
    rooms = r.getrooms()
    stage = "stage1"
    roomlist = rooms[stage]["normal"]
    for key in tree:
        #if the room is not the root
        if key != "A":
            #assign normal room
            room = rooms[stage]["normal"][randint(0,len(roomlist)-1)]
            
        #if the room is the root
        else:
            #assign spawn room
            room = rooms[stage]["spawn"][0]
        #room = room["tiles"]
        connected = m.getconnected(tree,key)
        tiles = room["tiles"]
        tiles = processroom(tiles,connected)
        
        room["tiles"] = tiles
        roomdict[key] = r.Room(room)
    #get the nodes where special rooms should be added
    specialdict = assignspecialrooms(tree)
    print(specialdict)
    for roomkey in specialdict:
        contents = specialdict[roomkey]
        room = rooms[stage][contents][randint(0,len(rooms[stage][contents])-1)]
        print()
        connected = m.getconnected(tree,roomkey)
        tiles = room["tiles"]
        tiles = processroom(tiles,connected)
        
        room["tiles"] = tiles
        roomdict[roomkey] = r.Room(room)
    
    return roomdict,specialdict

#saves the state of the current map into a dat file
def saverun(tree,roomdict,currentroom,exploredlist):
    file = open(PICKLEFILE,"wb")
    rundict = {"tree":tree,
               "roomdict":roomdict,
               "currentroom":currentroom,
               "exploredlist":exploredlist}
    pickle.dump(rundict,file)
    file.close()

#retrieves data from the dat file, to get a saved run
def getrun():
    file = open(PICKLEFILE,"rb")
    rundict = pickle.load(file)
    tree = rundict["tree"]
    roomdict = rundict["roomdict"]
    currentroom = rundict["currentroom"]
    exploredlist = rundict["exploredlist"]
    file.close()
    return tree,roomdict,currentroom,exploredlist                

#class that allows the smooth transition between rooms
class Roomtransition:
    def __init__(self):
        self.directions = ["n","e","s","w"]
        self.animdirectionunit = {"e":(-1,0),
                                 "n":(0,1),
                                 "w":(1,0),
                                 "s":(0,-1)}
        self.betweenroomanimate = False
        self.slip = 0.2
            
    #used to check if the transition should be started (i.e. if the player moves to a new room)
    def updatestart(self,explored,entities,player,surface,triggers,roomdict,tree,currentroom):
        direction = self.gettriggers(triggers)
        nextroom = self.getnextroom(direction,currentroom,tree)
        #start the transition if the player has moved to a new room
        if direction != None and nextroom and not self.betweenroomanimate:
            #set the position of each room surface
            self.unitmove = self.animdirectionunit[direction]
            self.unitmove = vector(self.unitmove)*((r.TILENUM*r.TILESIZE)-r.TILESIZE)*-1
            self.currentpos = vector(0,0)
            self.nextpos = self.unitmove
            entities.clearenemies()
            entities.clearprojectiles()
            
            self.updatescreen(player,surface,roomdict,currentroom)
            self.betweenroomanimate = True
            return nextroom
            
    #returns the direction that the screen is going to be moved in (based on where the player leaves the screen)
    #nothing is returned if the player is not moving to a new room
    def gettriggers(self,triggers):
        
        keytriggers = [K_UP,K_RIGHT,K_DOWN,K_LEFT]
        for trigger in triggers:
            if trigger in keytriggers:
                #uses self.directions to change what is in keytriggers to a string direction
                return self.directions[keytriggers.index(trigger)]

    #updates the surfaces for both rooms
    def updatescreen(self,player,surface,roomdict,currentroom):
        surface.fill((0,0,0))
        self.updatesprites(player,surface,roomdict,currentroom)
        #take a snapshot of the current screen
        self.currentsurface = surface.copy()

        #create a new surface and draw all the sprites on it that would normally be drawn directly onto the screen
        self.nextsurface = pygame.Surface((r.TILESIZE*r.TILENUM,r.TILESIZE*r.TILENUM))
        self.updatesprites(player,self.nextsurface,roomdict,self.nextroom)
        

    #updates the surface for the next room
    def updatesprites(self,player,surface,roomdict,currentroom):
        roomdict[currentroom].updatedecor(surface)
        e.entities.update(roomdict[currentroom].tilelist,player,surface)
        player.updatesprite(surface)
        roomdict[currentroom].update(surface)

    #checks that the direction that the transition happens in is possible(if there is a room there)
    #stores the next room that will be moved to if it is possible
    def getnextroom(self,direction,currentroom,tree):
        connected = m.getconnected3(tree,currentroom)
        for nodekey in connected:
            if connected[nodekey] == direction:
                self.nextroom = nodekey
                return True
        return False
        
    
    #updates the transition animation every frame that it is active
    def updateanimate(self,surface,roomdict,currentroom):
        #if the animation is taking place
        if self.betweenroomanimate:
            target = self.unitmove*-1
            #use lerp for smooth movement
            self.currentpos = self.currentpos.lerp(target,self.slip)
            self.nextpos = self.nextpos.lerp(vector(0,0),self.slip)
            #draw both rooms to the screen
            surface.blit(self.currentsurface,self.currentpos)
            surface.blit(self.nextsurface,self.nextpos)
            between = target-self.currentpos
            #print(between,between.magnitude())
            #lerp produces small values the longer it is used on itself, to make sure it doesn't slow the transition, I cut
            #the animation short to keep the transition snappy
            if self.currentpos == target or between.magnitude()<=2:
                currentroom = self.nextroom
                self.betweenroomanimate = False
            #change the current room
        return currentroom
    def intransition(self):
        return self.betweenroomanimate

#Part of the ui that shows the "map", which displays where the player is
#The minimap usually shows an enlarged section of the map on a small portion of the screen, showing rooms around the player
#The minimap can be enlarged with tab, which changes the shape of the map to take up a larger portion of the screen and
#show the whole map rather than just a small portion
class Minimap:
    def __init__(self):
        #big mode is used to toggle if the map should be enlarged or not
        self.bigmode = False
        self.bigtransition = False
        
        self.actualscroll = vector(0,0)
        self.bigmap = pygame.Surface((300,300))
        
        #used to detect if a new room has been moved to or if a room is entered for the first time
        self.previousexplored = []
        self.previoustree = []
        self.currentroom = ""
        self.transparency = 255
        pass
    def update(self,specialdict,keys,screen,tree,explored,currentroom,pos=(0,0)):
        adjacent = m.getunexplored(tree,explored)
        notinclude = m.getnotincluded(tree,explored)
        
        surface = pygame.Surface((100,70))
        surfacedims = surface.get_size()
        surfacemag = max(surfacedims[1],surfacedims[0])
        #determines how many times the pure image for the minimap is enlarged by
        magnification = 2
        surfacedims = vector(surfacemag*magnification,surfacemag*magnification)
        
        #if tab is pressed, expand the minimap
        if K_TAB in keys:
            self.bigmode = True
        else:
            self.bigmode = False
    

        #if the player moves between rooms
        if self.currentroom != currentroom or self.previousexplored != explored:
            #update the surface for the minimap
            self.surf = pygame.Surface(surfacedims)
            self.surf = m.generatemapsurface(tree,specialdict,self.surf,adjacent,True,notinclude,currentroom)
            self.updatebigmap(specialdict,tree,explored,currentroom)
            self.currentroom = currentroom
            self.previousexplored = explored.copy()
        #if the tree changes, change the coordinate dictionary
        if self.previoustree != tree:
            self.previoustree = tree
            self.coordict = m.generatecoorddict(tree)

        #if the minimap isn't expanded
        if not self.bigmode:
            #scroll the camera to the current room
            aimpos = self.coordict[currentroom]
            aimpos = vector(aimpos)* m.mapsurfacemultiplier(self.surf)

            self.actualscroll = lerp(self.actualscroll,aimpos,0.7)
            if (self.actualscroll-aimpos).magnitude()<=2:
                self.actualscroll = aimpos
                
            #draw the map surface onto minimap surface, applying camera movement
            self.surfrect = self.surf.get_rect()
            self.surfrect.center = -self.actualscroll + (vector(surface.get_size())/2)
            surface.blit(self.surf,self.surfrect)
            #draw minimap onto the screen
            self.surfacerect = surface.get_rect()
            self.surfacerect.topleft = pos
            surface.set_alpha(self.transparency)
            screen.blit(surface,pos)
        else:
            #darken the screen and draw the enlarged map to the middle of the screen
            shade = pygame.Surface(screen.get_size())
            shade.set_alpha(100)
            bigrect = self.bigmap.get_rect()
            bigrect.center = vector(screen.get_size())/2
            screen.blit(shade,(0,0))
            screen.blit(self.bigmap,bigrect)
    #used to update the surface of the enlarged map when it needs to be
    def updatebigmap(self,specialdict,tree,explored,currentroom):
        adjacent = m.getunexplored(tree,exploredlist)
        notinclude = m.getnotincluded(tree,exploredlist)
        self.bigmap.fill((0,0,0))
        self.bigmap = m.generatemapsurface(tree,specialdict,self.bigmap,adjacent,True,notinclude,currentroom)

    def changealpha(self,player,mousepos):
        mintrans = 80
        slip = 0.7
        if player.rect.colliderect(self.surfacerect) or self.surfacerect.collidepoint(mousepos):
            self.transparency = lerp(self.transparency,mintrans,slip)
        else:
            if not self.transparency == 255:
                self.transparency = lerp(self.transparency,255,slip)
        self.transparency = min(self.transparency,255)
            
        

#is used to toggle fullscreen and center the game to the middle of the screen
def initdisplay(gamesurf,screen,fullscreen=True,pixelperfect=False,windowedswitch=False):
    rect = gamesurf.get_rect()
    #changes the screen object to fullscreen based on the fullscreen variable
    if fullscreen:
        screensize = fullscreensize
        screen = pygame.display.set_mode(screensize,pygame.FULLSCREEN)
    else:
        if windowedswitch:
            screensize = (500,500)
        else:
            screensize = screen.get_size()
        screen = pygame.display.set_mode(screensize,pygame.RESIZABLE)
    #enlarges the screen up to 10 times, to find a scale(a multiplier to each pixel) that would work
    for tempscale in range(1,10+1):
        scalesize = vector(gamesize)*tempscale
        x = scalesize[0]>screensize[0]
        y = scalesize[1]>screensize[1]
        if x or y:
            scale = tempscale-1
            break
    #if the game cannot fit on the screen, raise an error
    if scale < 0:
        raise Exception ("screen display is too small")

    #finds the topleft position that the game should be so that it is centered
    rect= pygame.Rect((0,0),vector(gamesize)*scale)
    screenrect = pygame.Rect((0,0),screensize)
    rect.center = screenrect.center
    blitpos = rect.topleft
    return blitpos,scale

def updategamesprites():
    pass
tree = m.generatetree(12)
#starts the player at spawn, with no explored rooms
currentroom = "A"
exploredlist = []
roomdict,specialdict = treestorooms(tree)

keys = []

betweenroomanimate = False

clock = pygame.time.Clock()

transition = Roomtransition()

player = platformer.Player()
gun = platformer.Gun(player.pos)

minimap = Minimap()

#generates invisible tiles slightly outside the screen to stop the player going out of bounds
bordertiles = []

#create invisible border round the whole screen
for y in [-r.TILESIZE,r.TILENUM*r.TILESIZE]:
    for x in range(-r.TILESIZE,r.TILENUM*r.TILESIZE,r.TILESIZE):
        bordertiles.append(r.Tile((x,y)))
for x in [-r.TILESIZE,r.TILENUM*r.TILESIZE]:
    for y in range(-r.TILESIZE,r.TILENUM*r.TILESIZE,r.TILESIZE):
        bordertiles.append(r.Tile((x,y)))

#remove tiles from the invisible border that have an x or y coordinate in the middle of the room
median = r.TILENUM//2
newlist = []

fulltemp = fullscreen
for tile in bordertiles:
    if tile.rect.topleft[0] in range(median-2,median+2):
        pass
    elif tile.rect.topleft[1] in range(median-2,median+2):
        pass
    else:
        newlist.append(tile)
        
bordertiles = newlist

doortiles = []
for y in range(median-1,median+3):
    for x in range(0,r.TILENUM,r.TILENUM-1):
    
        doortiles.append(r.Tile((x,y-1),"gatetile1"))
        doortiles.append(r.Tile((y-1,x),"gatetile2"))

        

blitpos = (0,0)
scale = 1

gamesurf = pygame.Surface(gamesize)
blitpos,scale = initdisplay(gamesurf,screen,fullscreen)

inencounter = False

temproom = currentroom

dooranimtimer = Timer(5)
doorprogress = 0
#screen = pygame.display.set_mode(inttuple(vector(screenlength,screenlength)*2),pygame.RESIZABLE)
while True:
    
    mousepos = (vector(pygame.mouse.get_pos())-vector(blitpos))/scale
    #mousepos += vector(blitpos)
    gamesurf = pygame.Surface(gamesize)
    for event in pygame.event.get():
        #if there is any change in the window size (e.g. if the windowed screen is maximized)
        if event.type == pygame.VIDEORESIZE:
            blitpos,scale = initdisplay(gamesurf,screen,fullscreen,pixelperfect,False)                    
        #if the player presses the exit button on the window, close the window and stop the script        
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            keys.append(event.key)
        if event.type == pygame.KEYUP:
            try:
                keys.remove(event.key)
            except:
                pass
        
    if K_ESCAPE in keys:
        pygame.quit()
        sys.exit()
        
    if K_EQUALS in keys:
        keys.remove(K_EQUALS)
        
        fullscreen = not fullscreen
        blitpos,scale = initdisplay(gamesurf,screen,fullscreen,pixelperfect,True)
    #assign direction to triggers(arrow keys in this case)
    keydirections = [K_UP,K_RIGHT,K_DOWN,K_LEFT]
    directions = []
    screenrect = gamesurf.get_rect()
    lastx = (gamesurf.get_width()//r.TILESIZE)-1
    lasty = (gamesurf.get_height()//r.TILESIZE)-1

    #if there is not a transition animation already taking place
    if not transition.intransition():
        #if the player leaves through the top of the screen
        if player.rect.bottom < screenrect.top:
            directions.append(K_UP)
            player.rect.top = screenrect.bottom-(r.TILESIZE*2)
            player.velocity[1] = -7
        #if the player leaves through the bottom of the screen
        elif player.rect.top > screenrect.bottom:
            directions.append(K_DOWN)
            player.rect.bottom = screenrect.top+(r.TILESIZE*2)
        #if the player leaves through the left side of the screen
        elif player.rect.right < screenrect.left:
            #player.velocity[1] = 0
            player.rect.center = player.pos
            player.rect.y = min(193,player.rect.y)
            directions.append(K_LEFT)
            player.rect.left = screenrect.right-(r.TILESIZE*2)
        #if the player leaves through the right side of the screen
        elif player.rect.left > screenrect.right:
            player.rect.center = player.pos
            player.rect.y = min(193,player.rect.y)
            player.rect.right = screenrect.left+(r.TILESIZE*2)
            directions.append(K_RIGHT)
        player.updatepos()
        
    if not currentroom in exploredlist:
        exploredlist.append(currentroom)
        
    if not roomdict[currentroom].completed and not inencounter:
        doorprogress = 0
        inencounter = True
        for enemy in roomdict[currentroom].enemies:
            e.entities.add(e.Enemy(vector(enemy[1])*r.TILESIZE,enemy[0]))
    else:
        inencounter = False
        
        
    if e.entities.enemylist == []:
        if not roomdict[currentroom].completed:
            roomdict[currentroom].completed = True
        inencounter = False
        if not inencounter and dooranimtimer.update():
            dooranimtimer.reset()
            doorprogress -= 1
            
            
    else:
        if roomdict[currentroom].completed:
            e.entities.clearenemies()
        inencounter = True
        if doorprogress != 4 and dooranimtimer.update():
            dooranimtimer.reset()
            doorprogress += 1
            
    
    
    transition.updatestart(exploredlist,e.entities,player,gamesurf,directions,roomdict,tree,currentroom)

    temproom = currentroom
    #get new map, reset explored list and set current room to spawn
    if 32 in keys:
        tree = m.generatetree(12)
        currentroom = "A"
        exploredlist = []
        roomdict, specialdict = treestorooms(tree)
        keys.remove(32)
    if K_1 in keys:
        saverun(tree,roomdict,currentroom,exploredlist)
    if K_2 in keys:
        tree,roomdict,currentroom,exploredlist = getrun()
    if K_e in keys:
        player.pos = mousepos
        
        player.velocity = [0,0]
    if K_q in keys:
        player.velocity = [0,-20]
    if K_p in keys:
        pixelperfect = not pixelperfect
        blitpos,scale = initdisplay(gamesurf,screen,fullscreen)
        keys.remove(K_p)
    if K_c in keys:
        e.entities.clearenemies()

    #debug text
    quick.print("space:reset")
    quick.print("1:save")
    quick.print("2:load")
    quick.print("e:teleport to mouse")
    quick.print("q:upwards velocity")
    quick.print("p:pixelperfect")
    quick.print("+:toggle fullscreen")
    quick.print("c:clear enemies")
        
    #if add current room to explored rooms if it has not already been explored
    
    #draw black over the whole screen
    screen.fill((0,0,0))
    clock.tick(80)
    #draw current room object to screen
    currentroom = transition.updateanimate(gamesurf,roomdict,currentroom)
    
    if pygame.mouse.get_pressed()[0]:
        if player.canshoot():
            playerpos = vector(gun.pos)
            angle = vector(0,0).angle_to(mousepos-playerpos)
            e.entities.add(e.Projectile(playerpos,0,1,(0,0),angle,player.shotspeed))
        
    #if there is no transition animation, update sprites normally
    if not transition.intransition():
        tiles = roomdict[currentroom].tilelist+bordertiles
        if inencounter:
            tiles += doortiles
        roomdict[currentroom].updatedecor(gamesurf)
        if doorprogress != 0:
            for num in range(0,((doorprogress-1)*4)+1,4):
                for num2 in range(4):
                    doortiles[num+num2].update(gamesurf)
        
        roomdict[currentroom].update(gamesurf)
        
        e.entities.update(tiles,player,gamesurf)
        player.update(tiles,gamesurf,keys)
        gun.update(gamesurf,player,mousepos)
        
        
            
    
    #screen.blit(pygame.transform.scale2x(pygame.transform.scale(screen,inttuple(vector(screen.get_size())))),(0,0))
    quick.print("fps:",int(clock.get_fps()))
    quick.print("projectiles:",len(e.entities.projectilelist))
    quick.print("playerdx:",round(player.deltax))

    
    #screen.blit(pygame.transform.scale(screen,inttuple(vector(screen.get_size())*2)),(0,0))
    if K_p in keys:
        now = datetime.now()
        name = now.strftime("%Y%_m%_d%_H%M%S")
        tooutput = pygame.transform.scale(screen,inttuple(vector(gamesurf.get_size())*2))
        pygame.image.save(tooutput,"output/"+name+".png")
        keys.remove(K_p)

    quick.update(gamesurf)
    #update minimap
    
    minimap.update(specialdict,keys,gamesurf,tree,exploredlist,currentroom)
    minimap.changealpha(player,mousepos)
    #stretches the game to fit the screen, if pixel perfect mode is not being used
    if not pixelperfect:
        screenrect = screen.get_rect()
        lengthsize = min(screen.get_width(),screen.get_height())
        gamesurf = pygame.transform.scale(gamesurf,inttuple(vector(lengthsize,lengthsize)))
        gamerect = gamesurf.get_rect()
        gamerect.center = screenrect.center
        blitpos = gamerect.topleft
    #scales the screen up pixel perfectly,(so that each pixel is a square)
    
    else:
        if scale > 1:
            gamesurf = pygame.transform.scale(gamesurf,inttuple(vector(gamesurf.get_size())*scale))
            pass
    screen.blit(gamesurf,blitpos)
    #update the screen
    pygame.display.flip()
    
    #if key is an input key, remove it so that it does not continually cause procedures to be run
    for key in keys:
        if key in keydirections:
            keys.remove(key)

    temproom = currentroom
