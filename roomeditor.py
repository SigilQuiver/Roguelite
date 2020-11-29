#note - this script will not be in the end product but is for me to produce rooms easier

import pygame
from pygame.locals import *
from math import *
from vector import *
import sys

import room1 as r

pygame.init()
screenlength = r.TILESIZE*20
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
    """
    #get an empty room, relative to the screen size
    #get what one row of tiles filling the whole screen as a string representation
    emptyrow = ""
    for num in range(screen.get_width()//TILESIZE):
        emptyrow += "0"
    #fill a room list with the empty string representations
    room = []
    for num in range(screen.get_height()//TILESIZE):
        room.append(emptyrow)
    """
    tiles = []
    keys = []
    tileid = 1
    while not finished:
        
        clock.tick(120)
        for event in pygame.event.get():
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
            if 32 in keys:
                keys.remove(32)
                finished = True
            if K_t in keys:
                tileid = int(input("enter tileid:"))

        #get the mouse position and the state of the LMB and RMB
        mousepos = pygame.mouse.get_pos()
        mousepressed1 = pygame.mouse.get_pressed()[0]
        mousepressed2 = pygame.mouse.get_pressed()[2]
        pos = vector(mousepos)//TILESIZE
        #if LMB is pressed, add a tile at position of mouse
        if mousepressed1:
            tiles.append([tileid,list(pos)])
        #if RMB is pressed, remove a tile at position of mouse
        if mousepressed2:
            toremove = []
            for tile in tiles:
                tilepos = tile[1]
                if tilepos == pos:
                    toremove.append(tile)
            for tile in toremove:
                tiles.remove(tile)
                         
        #draw room to screen and refresh it
        temproom = r.Room(tiles)
        temproom.update(screen)
        pygame.display.flip()
        screen.blit(back,(0,0))
    #if the key exists already, add it to the existing list at that key
    room = {"tiles":tiles}
    try:
        print(key,key2)
        dictroom[key][key2].append(room)
    #if the key does not exist create a list at that key, then add to that list
    except:
        dictroom[key][key2] = [room]
        #dictroom[key].append(tiles)
    #save the new dictionary to the file in a formatted way
    r.writefile(dictroom)
    #make the screen green to show success
    screen.fill((3,170,3))
    pygame.display.flip()
r.writefile(dictroom)
