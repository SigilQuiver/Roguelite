#note - this script will not be in the end product but is for me to produce rooms easier

import pygame
from pygame.locals import *
from math import *
from vector import *
from menu import *
from text import *

import sys

import room1 as r

pygame.init()
screenlength = r.TILESIZE*r.TILENUM
screen = pygame.display.set_mode((screenlength,screenlength),pygame.RESIZABLE)
back = pygame.Surface(screen.get_size())
clock = pygame.time.Clock()

#get the size of the tiles in the room module
TILESIZE = r.TILESIZE
#get all the rooms from the text file as a dictionary
dictroom = r.getrooms()

while True:
    #get key name
    print("stages:",dictroom.keys())
    key = input("stage type (key):")
    #if exit or save is inputted, exit program
    roomtypes = dictroom[key]
    print("roomtypes",roomtypes.keys())
    key2 = input("room type (key):")
    if key in ["exit","save"] or key2 in key in ["exit","save"]:
        break
    finished = False
    choice = input("new(y,n):").lower()
    new = choice == "y"
    if not new:
        roomid = 0
        if len(dictroom[key][key2][roomid]) != 0:
            tiles = dictroom[key][key2][roomid]["tiles"]
            try:
                enemies = dictroom[key][key2][roomid]["enemies"]
            except:
                enemies = []
            
        else:
            finished = True
    else:
        tiles = []
        enemies = []
    keys = []
    tileid = 1
    mode = ["enemies","tiles","items"]
    while not finished:
        quick.print("use q to switch between enemies,tiles and items")
        quick.print("mode:",mode[0])
        quick.print("use plus and minus to increase or decrease id")
        quick.print("id:",tileid)
        
        if K_MINUS in keys:
            keys.remove(K_MINUS)
            tileid -= min(tileid-1,1)
        elif K_EQUALS in keys:
            keys.remove(K_EQUALS)
            tileid += 1
        if K_q in keys:
            keys.remove(K_q)
            mode.append(mode.pop(0))
            
        if not new:
            quick.print("use delete to delete a room")
            quick.print("use arrow keys to navigate rooms")
            quick.print("roomid:",roomid)
        clock.tick(120)
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((screenlength,screenlength),pygame.RESIZABLE)
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
            #if space is pressed, exit finished loop
        if K_RETURN in keys:
            keys.remove(K_RETURN)
            finished = True
        if K_t in keys:
            tileid = int(input("enter tileid:"))
        if new and len(dictroom[key][key2]) == 0:
            break
        if not new:
            if K_LEFT in keys:
                keys.remove(K_LEFT)
                dictroom[key][key2][roomid]["tiles"] = tiles
                dictroom[key][key2][roomid]["enemies"] = enemies
                roomid = max(0,roomid-1)
                tiles = dictroom[key][key2][roomid]["tiles"]
                try:
                    enemies = dictroom[key][key2][roomid]["enemies"]
                except:
                    enemies = []
            if K_RIGHT in keys:
                keys.remove(K_RIGHT)
                dictroom[key][key2][roomid]["tiles"] = tiles
                dictroom[key][key2][roomid]["enemies"] = enemies
                roomid = min(len(dictroom[key][key2])-1,roomid+1)
                tiles = dictroom[key][key2][roomid]["tiles"]
                try:
                    enemies = dictroom[key][key2][roomid]["enemies"]
                except:
                    enemies = []
            if K_DELETE in keys:
                keys.remove(K_DELETE)
                dictroom[key][key2].pop(roomid)
                if len(dictroom[key][key2]) == 0:
                    break
                roomid = 0
                tiles = dictroom[key][key2][roomid]["tiles"]
                try:
                    enemies = dictroom[key][key2][roomid]["enemies"]
                except:
                    enemies = []
            
        
        #get the mouse position and the state of the LMB and RMB
        mousepos = pygame.mouse.get_pos()
        mousepressed1 = pygame.mouse.get_pressed()[0]
        mousepressed2 = pygame.mouse.get_pressed()[2]
        pos = vector(mousepos)//TILESIZE
        #if LMB is pressed, add a tile at position of mouse
        if mousepressed1:
            if mode[0] == "enemies":
                if [tileid,list(pos)] not in tiles:
                    enemies.append([tileid,list(pos)])
            if mode[0] == "tiles":
                if [tileid,list(pos)] not in tiles:
                    tiles.append([tileid,list(pos)])
        #if RMB is pressed, remove a tile at position of mouse
        if mousepressed2:
            if mode[0] == "tiles":
                toremove = []
                for tile in tiles:
                    tilepos = tile[1]
                    if tilepos == pos:
                        toremove.append(tile)
                for tile in toremove:
                    tiles.remove(tile)
            if mode[0] == "enemies":
                toremove = []
                for enemy in enemies:
                    enemypos = enemy[1]
                    if enemypos == pos:
                        toremove.append(enemy)
                for enemy in toremove:
                    enemies.remove(enemy)

       
        #draw room to screen and refresh it
        temproom = r.Room({"tiles":tiles})
        temproom.update(screen)
        for enemy in enemies:
            string = "ene"+str(enemy[0])+"  "
            numbersurf = changecolour(textgen.generatetext(string),(0,0,0),(255,30,10))
            screen.blit(numbersurf,vector(enemy[1])*r.TILESIZE)
            
        existing = []
        for enemy in enemies:
            if enemy not in existing:
                existing.append(enemy)
        enemies = existing
        
        quick.update(screen)
        pygame.display.flip()
        screen.blit(back,(0,0))
    #if the key exists already, add it to the existing list at that key
    screenrect = screen.get_rect()
    newtilelist = []
    for num in range(len(tiles)):
        tile = tiles[num]
        tilerect = r.Tile(tile[1],tile[0]).rect
        if not tilerect.colliderect(screenrect):
            newtilelist.append(tile)
            
    room = {"tiles":tiles,"enemies":enemies}
    if new:
        try:
            dictroom[key][key2].append(room)
        #if the key does not exist create a list at that key, then add to that list
        except:
            dictroom[key][key2] = [room]
            #dictroom[key].append(tiles)
    else:
        dictroom[key][key2][roomid] = room
    #save the new dictionary to the file in a formatted way
    r.writefile(dictroom)
    #make the screen green to show success
    screen.fill((3,170,3))
    pygame.display.flip()
r.writefile(dictroom)
