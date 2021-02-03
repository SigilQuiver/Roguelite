    #this is the main script for the game, which uses all the other modules
import pygame
from pygame.locals import *
from pygame._sdl2.video import Window

import time
from datetime import datetime
import sys
from random import *

import map1 as m
import room1 as r
import entities as e
import items as i
import platformer

from menu import *
from vector import *

from unlocks import *

import pickle
    
#adds borders to a tuple representation of a room, leaving holes where the player can move to different rooms
#the gaps will changed based on which direction the room is coming from
def processroom(room,directions,stage):
    #get the furthest grid coordinates at the edge of the screen
    last = r.TILENUM-1
    tiles = room
    #change the tile appearance based on what stage the player is on (unused)
    tiletype = 1
    if stage == "stage2":
        tiletype = 2
    if stage == "stage3":
        tiletype = 3
    #creates a border of tiles around the whole room
    for x in range(0,last+1,last):
        for y in range(last+1):
            occurances = 0
            for tile in tiles:
                if tile[1] == (x,y):
                    occurances =1
            if occurances == 0:
                tiles.append((tiletype,(x,y)))
    for y in range(0,last+1,last):
        for x in range(last+1):
            occurances = 0
            for tile in tiles:
                if tile[1] == (x,y):
                    occurances =1
            if occurances == 0:
                tiles.append((tiletype,(x,y)))
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
                rejected.append((tiletype,(coords)))
        
        if direction == "e":
            for x in range(-1,3):
                coords = (last,median+x)
                rejected.append((tiletype,(coords)))
        
        if direction == "n":
            for x in range(-1,3):
                coords = (median+x,0)
                rejected.append((tiletype,(coords)))
        if direction == "s":
            for x in range(-1,3):
                coords = (median+x,last)
                rejected.append((tiletype,(coords)))
                
    #adds all tiles except the ones in the list "rejected" to a new list
    newroom = []
    for tile in tiles:
        if tile not in rejected:
            newroom.append(tile)

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
def treestorooms(tree,items,newrun=False,stage = "stage1"):
    roomdict = {}
    rooms = r.getrooms()
    
    roomlist = rooms[stage]["normal"]
    for key in tree:
        #if the room is not the root
        if key != "A":
            #assign normal room
            room = rooms[stage]["normal"][randint(0,len(roomlist)-1)]
            
        #if the room is the root
        else:
            #assign spawn room
            room = rooms[stage]["spawn"][randint(0,len(rooms[stage]["spawn"])-1)]
        
        connected = m.getconnected(tree,key)
        tiles = room["tiles"]
        tiles = processroom(tiles,connected,stage)
        
        room["tiles"] = tiles
        roomdict[key] = r.Room(room)
        if "items" in room.keys() and newrun:
            for item in room["items"]:
                items.add(key,item[1])
    #get the nodes where special rooms should be added
    specialdict = assignspecialrooms(tree)
    
    for roomkey in specialdict:
        contents = specialdict[roomkey]
        room = rooms[stage][contents][randint(0,len(rooms[stage][contents])-1)]
        connected = m.getconnected(tree,roomkey)
        tiles = room["tiles"]
        tiles = processroom(tiles,connected,stage)
        
        room["tiles"] = tiles
        
        if "items" in room.keys() and newrun:
            for item in room["items"]:
                items.add(roomkey,item[1])
                
        roomdict[roomkey] = r.Room(room)
    
    return roomdict,specialdict,items

#saves the state of the current map into a dat file
def saverun(tree,roomdict,currentroom,exploredlist,specialdict,items,player,stages,difficulty,coins):
    file = open(PICKLEFILE,"wb")
    rundict = {"tree":tree,
               "roomdict":roomdict,
               "currentroom":currentroom,
               "exploredlist":exploredlist,
               "specialdict":specialdict,
               "items":items,
               "maxhp":player.maxhp,
               "hp":player.hp,
               "stages":stages,
               "difficulty":difficulty,
               "coins":coins}
    pickle.dump(rundict,file)
    file.close()

#retrieves data from the dat file, to get a saved run
def getrun(player):
    file = open(PICKLEFILE,"rb")
    rundict = pickle.load(file)
    tree = rundict["tree"]
    roomdict = rundict["roomdict"]
    currentroom = rundict["currentroom"]
    exploredlist = rundict["exploredlist"]
    specialdict = rundict["specialdict"]
    items = rundict["items"]
    player.maxhp = rundict["maxhp"]
    player.hp = rundict["hp"]
    difficulty = rundict["difficulty"]
    stages = rundict["stages"]
    coins = rundict["coins"]
    file.close()
    return tree,roomdict,currentroom,exploredlist,specialdict,items,difficulty,stages,coins     

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
    def updatestart(self,explored,entities,player,surface,triggers,roomdict,tree,currentroom,unlocks):
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
            entities.clearprojectiles(entities)
            
            self.updatescreen(player,surface,roomdict,currentroom,unlocks)
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
    def updatescreen(self,player,surface,roomdict,currentroom,unlocks):
        surface.fill((0,0,0))
        self.updatesprites(player,surface,roomdict,currentroom,unlocks)
        #take a snapshot of the current screen
        self.currentsurface = surface.copy()

        #create a new surface and draw all the sprites on it that would normally be drawn directly onto the screen
        self.nextsurface = pygame.Surface((r.TILESIZE*r.TILENUM,r.TILESIZE*r.TILENUM))
        self.updatesprites(player,self.nextsurface,roomdict,self.nextroom,unlocks)
        

    #updates the surface for the next room
    def updatesprites(self,player,surface,roomdict,currentroom,unlocks):
        roomdict[currentroom].updatedecor(surface)
        e.entities.update(roomdict[currentroom].tilelist,player,surface,unlocks)
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
            self.surfacerect.topright = screen.get_rect().topright
            surface.set_alpha(self.transparency)
            screen.blit(surface,self.surfacerect)
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
def initdisplay(menu,screen,windowedswitch=False):
    optiondict = menu.getoptions()
    #changes the screen object to fullscreen based on the fullscreen variable
    if optiondict["fullscreen"]:
        screensize = optiondict["fullscreen resolution"]
        screen = pygame.display.set_mode(screensize,pygame.FULLSCREEN)
    else:
        screensize = screen.get_size()
        if screensize[0]>=pygame.display.list_modes()[0][0] and screensize[1]>=pygame.display.list_modes()[0][1]:
            screensize = (pygame.display.list_modes()[0][0]-200,pygame.display.list_modes()[0][1]-200)
        screen = pygame.display.set_mode(screensize,pygame.RESIZABLE)
    return screen

def getbordertilesanddoortiles():
    #generates invisible tiles slightly outside the screen to try and stop the player going out of bounds
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
    return bordertiles,doortiles

def moveplayertransition(gamesurf,transition,player):
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
    return directions
def resizemenu(pixelperfect,screensurf,mousepos2,menu,scale):
    screenscale = (min(screen.get_width(),screen.get_height())/GAMESIZE[0])
    if pixelperfect:
        screensurf = getscreensurf(screen,scale)
        mousepos2 = (vector(pygame.mouse.get_pos()))/scale
    else:
        screensurf = getscreensurf(screen,scale)
        mousepos2 = (vector(pygame.mouse.get_pos()))/scale
    menu.reposition(screensurf)
    return pixelperfect,screensurf,mousepos2,menu,scale
#the file to which a current playthrough will be saved to
PICKLEFILE = "run.dat"

#initialize pygame
pygame.init()

screenlength = r.TILESIZE*r.TILENUM
GAMESIZE = (screenlength,screenlength)
fullscreen = True
pixelperfect = True

screen = pygame.display.set_mode((screenlength,screenlength),pygame.RESIZABLE)
fullscreensize = pygame.display.list_modes()[0]
background = pygame.Surface(screen.get_rect().size)

ROOMNUM = 12
tree = m.generatetree(ROOMNUM)
#starts the player at spawn, with no explored rooms
currentroom = "A"
previousroom = currentroom
exploredlist = []
unlocks = Unlocks()
items = i.Items(unlocks)
itemui = i.Itemview()
#items.add("A",(90,90))

roomdict,specialdict,items = treestorooms(tree,items,True)

coins = i.Coins()

keys = []

clock = pygame.time.Clock()

transition = Roomtransition()

player = platformer.Player()
gun = platformer.Gun(player.pos)

minimap = Minimap()

bordertiles,doortiles = getbordertilesanddoortiles()

blitpos = (0,0)
scale = 1

menu = Menu(screen)
gamemenu = Gamemenu(screen)

state = "menu"

gamesurf = pygame.Surface(GAMESIZE)
initdisplay(menu,screen)

heart = Hearts()

inencounter = False

temproom = currentroom

dooranimtimer = Timer(5)
doorprogress = 0

gundir = "left"



mousepos2 = (0,0)

#pixelperfect,screensurf,mousepos2,menu,scale = resizemenu(pixelperfect,screensurf,mousepos2,menu,scale)

scale = min(screen.get_width(),screen.get_height())/GAMESIZE[0]
tempscale = int(scale)
dims = inttuple((vector(screen.get_size())/scale))
toblitrect = pygame.Rect((0,0),dims)
toblit = pygame.Surface(dims)
toblit.fill((0,0,0))

gameoffset = (0,0)
screenoffset = (0,0)

stages = ["stage2","stage3","stage1","stage2"]

gameover = Gameover(toblit)

difficulty = "normal"



haswon = False
while True:
    #reset the image the game is drawn onto
    gamesurf = pygame.Surface(GAMESIZE)

    #gets the mouse positions based on the scale of the game or if it is not pixel perfect
    scale = min(screen.get_width(),screen.get_height())/GAMESIZE[0]
    tempscale = int(scale)
    mousepos = (vector(pygame.mouse.get_pos())-vector(screenoffset))
    mousepos2 = (vector(pygame.mouse.get_pos())-vector(screenoffset))
    if scale > 1:
        if menu.getoptions()["pixel-perfect"]:
            mousepos = mousepos/tempscale
            mousepos2 = mousepos2/tempscale
        else:
            mousepos = mousepos/scale
            mousepos2 = mousepos2/scale
    mousepos = mousepos-vector(gameoffset)
        
    for event in pygame.event.get():
        #if there is any change in the window size (e.g. if the windowed screen is maximized)
        if event.type == pygame.VIDEORESIZE:
            if state == "menu":
                initdisplay(menu,screen)
            elif state == "gamemenu" or state == "game":
                initdisplay(gamemenu,screen)
            
        #if the player presses the exit button on the window, close the window and stop the script        
        if event.type == pygame.QUIT:
            if state == "game" or state == "gamemenu":
                saverun(tree,roomdict,previousroom,exploredlist,specialdict,items,player,stages,difficulty,coins)
                unlocks.writesave()
            pygame.quit()
            sys.exit()

        #store key presses in a list
        if event.type == pygame.KEYDOWN:
            keys.append(event.key)
        if event.type == pygame.KEYUP:
            try:
                keys.remove(event.key)
            except:
                pass
    
    
    clock.tick(80)

    
    #if escape is pressed ingame, open the menu, close the menu if it is pressed in the game menu
    #close the game if it is pressed in the main menu
    if K_ESCAPE in keys:
        keys.remove(K_ESCAPE)
        menu.__init__(toblit)
        gamemenu.__init__(toblit)
        if state in ["menu","gameover"]:
            pygame.quit()
            sys.exit()
        elif state == "gamemenu":
            state = "game"
        elif state == "game":
            state = "gamemenu"

    #the starts the game over screen if the player dies
    if player.hp <= 0 and state == "game":
            state = "gameover"
            
    #takes a screenshot when p is pressed, will cause an error if there is no output file
    if K_p in keys:
        now = datetime.now()
        name = now.strftime("%d_%m_%Y_%H %M %S")
        tooutput = screen
        pygame.image.save(tooutput,"output/"+name+".png")
        keys.remove(K_p)

    #main loop for the actual game
    if state == "game":
        #if the player reaches stage 2, unlock achievement
        if 3-len(stages) == 1:
            unlocks.progressachievement(3)

        #once all enemies are defeated in a room
        if roomdict[currentroom].completed:
            #keeps track of the previous room, so that if the player is in a room with enemies,
            #but saves in that room, they will spawn in the previous room that has no enemies when entering the game again
            previousroom = currentroom
            #removes all enemy projectiles in the room 
            e.entities.clearprojectiles(e.entities)
            
        #make the current room not greyed out on the map
        if not currentroom in exploredlist:
            exploredlist.append(currentroom)

        #if the room has not already been completed, and no enemies have been spawned, spawn enemies
        if not roomdict[currentroom].completed and not inencounter:
            doorprogress = 0
            inencounter = True
            for enemy in roomdict[currentroom].enemies:
                e.entities.add(e.Enemy(vector(enemy[1])*r.TILESIZE,enemy[0],(0,0),0,0,difficulty,3-len(stages)))
        else:
            inencounter = False
            
        #if there are no enemies in the room, mark it as completed
        if e.entities.enemylist == []:
            if not roomdict[currentroom].completed:
                roomdict[currentroom].completed = True
            inencounter = False
            #retract the doors
            if not inencounter and dooranimtimer.update():
                dooranimtimer.reset()
                doorprogress -= 1   
        else:
            if roomdict[currentroom].completed:
                e.entities.clearenemies()
            inencounter = True
            #close the doors
            if doorprogress != 4 and dooranimtimer.update():
                dooranimtimer.reset()
                doorprogress += 1
                
        #checks if the player is moving to another room
        directions = moveplayertransition(gamesurf,transition,player)
        transition.updatestart(exploredlist,e.entities,player,gamesurf,directions,roomdict,tree,currentroom,unlocks)
        currentroom = transition.updateanimate(gamesurf,roomdict,currentroom)

        #(debug use) kills all enemies in the room
        if K_c in keys:
            e.entities.clearenemies(unlocks,coins)
        
        
        
        
        nextstage = False
        #if there is no transition animation, update sprites normally
        if not transition.intransition():
            #get the tiles to be collided with
            #bordertiles is an invisible set of tiles used to prevent the player get out of the room other than through the entry spaces provided
            tiles = roomdict[currentroom].tilelist+bordertiles
            #add the door tiles to the collision if they are there
            if inencounter:
                tiles += doortiles
                
            #draw the decor(non collidable tiles)
            roomdict[currentroom].updatedecor(gamesurf)
            #draw the door tiles to the screen
            if doorprogress != 0:
                for num in range(0,((doorprogress-1)*4)+1,4):
                    for num2 in range(4):
                        doortiles[num+num2].update(gamesurf)

            #draw the current rooms tiles(and doors if they are there)
            #this method returns true when the player accepts a prompt at a door
            nextstage = roomdict[currentroom].update(gamesurf,player,keys,roomdict[currentroom].completed,e.entities)
            #update currency
            coins.update(gamesurf,player,e.entities,inencounter)
            #update enemies
            e.entities.update(tiles,player,gamesurf,unlocks,coins)
            #update items
            items.update(gamesurf,player,e.entities,currentroom,specialdict,coins,keys)
            #if a new item has been collected, change the player's stats
            if items.changestats:
                player.changestats(items)
            #update the player with the tiles to be collided with
            player.update(gun.direction,tiles,gamesurf,keys)
            #update the player's gun
            gun.update(e.entities,gamesurf,player,mousepos)
            

        #work out the pixel perfect scale of the current screen size
        scale = min(screen.get_width(),screen.get_height())/GAMESIZE[0]
        tempscale = int(scale)
        newdims = inttuple(vector(toblit.get_size())*tempscale)
        gamesurfrect = gamesurf.get_rect()
        gamesurfrect.center = toblitrect.center
        gameoffset = gamesurfrect.topleft
        
        
        #gamesurf is an image where only gameplay is drawn
        #toblit is upscaled when it is being drawn to the main screen, it is where everything has to eventually be blitted to
        #draw gamesurf onto toblit
        toblit.blit(gamesurf,gamesurfrect)
        
        #draw item ui
        itemrect = pygame.Rect((0,0),(22*4,22*8))
        itemrect.bottomleft = toblitrect.bottomleft
        itemui.update(toblit,itemrect,items,mousepos2,False)
        #draw minimap
        minimap.update(specialdict,keys,toblit,tree,exploredlist,currentroom)
        #draw heart meter
        heart.update(toblit,player.hp,player.maxhp,(1,1))
        #draw the number of coins the player has
        coins.counter(toblit,(0,22))
        
        #move to the next stage, if the player was on stage 3, win the game
        if nextstage:
            
            if not len(stages) == 0:
                #reset the map, but not the player's items
                items.reset()
                tree = m.generatetree(ROOMNUM)
                currentroom = "A"
                exploredlist = []
                roomdict,specialdict,items = treestorooms(tree,items,True,stages[0])
                transition = Roomtransition()
                player = platformer.Player()
                player.changestats(items)
                player.hp = player.maxhp
                gun = platformer.Gun(player.pos)
                stages.pop(0)
                nextstage = False
            else:
                haswon = True
                state = "gameover"
        
    #loop for the in-game menu
    elif state == "gamemenu":
        #puts PAUSED at the top of the screen
        titletext = generatetext("paused",None,"big",(0,0),(192,192,192))
        titlerect = titletext.get_rect()
        titlerect.center = (toblit.get_width()//2,10)
        toblit.blit(titletext,titlerect)
        
        #update the buttons for the game menu
        gamemenu.update(toblit,mousepos2,inttuple(vector(toblit.get_size())/2)[0])
        buttons = gamemenu.getbuttonresults()
        #the "if key == text:" is called if a certain button with that text is pressed
        for key in buttons:
            result = buttons[key]
            if result:
                if key == "return":
                    #unpause
                    state = "game"
                if key == "apply":
                    #apply and save the player's settings
                    initdisplay(gamemenu,screen)
                if key == "menu":
                    #go back to the main menu
                    menu.__init__(toblit)
                    state = "menu"
                    saverun(tree,roomdict,previousroom,exploredlist,specialdict,items,player,stages,difficulty,coins)
                    unlocks.writesave()
                if key == "save":
                    saverun(tree,roomdict,previousroom,exploredlist,specialdict,items,player,stages,difficulty,coins)
                    unlocks.writesave()
                if key == "exit":
                    saverun(tree,roomdict,previousroom,exploredlist,specialdict,items,player,stages,difficulty,coins)
                    unlocks.writesave()
                    pygame.quit()
                    sys.exit()
        #if in see unlocks part of the menu
        if "see unlocks" in gamemenu.currentstates:
            #draw the unlocks ui
            unlocks.drawunlocks(toblit,mousepos2)
            
    #loop for the starting menu
    elif state == "menu":
        titletext = generatetext("generic platformer roguelite",None,"big",(0,0),(192,192,192))
        titlerect = titletext.get_rect()
        titlerect.center = (toblit.get_width()//2,10)
        toblit.blit(titletext,titlerect)
        
        menu.update(toblit,mousepos2,inttuple(vector(toblit.get_size())/2)[0])
        buttons = menu.getbuttonresults()
        for key in buttons:
            result = buttons[key]
            
            if result:
                if key == "apply":
                    #apply and save the player's settings
                    initdisplay(menu,screen)
                    menu.reposition(toblit)
                if key == "exit":
                    pygame.quit()
                    sys.exit()
                if key == "newgame":
                    #reset the map and the player's items and start the game up
                    difficulty = menu.getoptions()["difficulty"]
                    stages = ["stage1","stage1"]
                    items.reset()
                    items.resetcollection()
                    tree = m.generatetree(ROOMNUM)
                    currentroom = "A"
                    exploredlist = []
                    roomdict,specialdict,items = treestorooms(tree,items,True)
                    transition = Roomtransition()
                    player = platformer.Player()
                    gun = platformer.Gun(player.pos)
                    coins = i.Coins()
                    state = "game"
                if key == "savedgame":
                    #load the map and player's items from the save file.
                    items.reset()
                    gamemenu.reposition(toblit)
                    tree,roomdict,currentroom,exploredlist,specialdict,items,difficulty,stages,coins = getrun(player)
                    player.changestats(items)
                    state = "game"
            #if in see unlocks part of the menu
            if "see unlocks" in menu.currentstates:
                #draw the unlocks ui
                unlocks.drawunlocks(toblit,mousepos2)
    #if the player wins/loses
    elif state == "gameover":
        #change title if the player won/lost
        if haswon:
            titletext = generatetext("you won",None,"big",(0,0),(192,192,192))
            msg = "well done!!!"
        else:
            titletext = generatetext("you lost",None,"big",(0,0),(192,192,192))
            msg = "better luck next time!"
        ypointer = 10
        titlerect = titletext.get_rect()
        titlerect.center = (toblit.get_width()//2,ypointer)
        toblit.blit(titletext,titlerect)
        
        ypointer += 20
        #draws text to the screen using a list, going down on the center of the screen
        #the text is just a couple of stats from the playthrough
        stats = [
            msg,
            " ",
            "mode:"+str(difficulty),
            "hits taken:"+str(player.hitstaken),
            "items collected:"+str(len(items.collected))
            ]
        for stat in stats:
            text = generatetext(stat,None,"small",(0,0),(192,192,192))
            textrect = titletext.get_rect()
            textrect.center = (toblit.get_width()//2,ypointer)
            toblit.blit(text,textrect)
            ypointer += 9
        gameover.update(toblit,mousepos2,inttuple(vector(toblit.get_size())/2)[0])
        buttons = gameover.getbuttonresults()
        #update buttons that return the player to the main menu
        for key in buttons:
            result = buttons[key]
            if result:
                if key == "menu":
                    menu.__init__(toblit)
                    state = "menu"
                    saverun(tree,roomdict,previousroom,exploredlist,specialdict,items,player,stages,difficulty)
                    unlocks.writesave()
                if key == "exit":
                    saverun(tree,roomdict,previousroom,exploredlist,specialdict,items,player,stages,difficulty)
                    unlocks.writesave()
                    pygame.quit()
                    sys.exit()

    #print the performance of the game onscreen
    quick.print("fps:",int(clock.get_fps()))
    quick.update(toblit)
    
    optionsdict = menu.getoptions()
    
    #reset the screen
    screen.fill((0,0,0))

    #scale the image "toblit" to the actual display based on if the game is in pixelperfect mode or not
    scale = min(screen.get_width(),screen.get_height())/GAMESIZE[0]
    tempscale = int(scale)
    #error messages if the size if the window is too small
    if scale < 1:
        string = "window is too small"
        if screen.get_width()//GAMESIZE[0] == 0:
            string+= "   "
            string+= "increase the width of window"
        if screen.get_height()//GAMESIZE[0] == 0:
            string+= "   "
            string+= "increase the height of window"
            
        generatetext(string,screen,"big",(1,1),(192,192,192))
    else:
        

        screenrect = screen.get_rect()
        if menu.getoptions()["pixel-perfect"]:
            newdims = inttuple(vector(toblit.get_size())*tempscale)
            
        else:
            newdims = inttuple(vector(toblit.get_size())*scale)
        toblit = pygame.transform.scale(toblit,newdims)
        toblitrect = toblit.get_rect()
        toblitrect.center = screenrect.center
        screenoffset = toblitrect.topleft
        screen.blit(toblit,toblitrect)
        
    #update the screen
    pygame.display.flip()

    #reset the display by filling it with the colour black
    
    dims = inttuple((vector(screen.get_size())/scale))
    toblitrect = pygame.Rect((0,0),dims)
    toblit = pygame.Surface(dims)
    toblit.fill((0,0,0))
    

    
