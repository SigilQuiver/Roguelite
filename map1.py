#NOTE: this module would be called "map", but map is a built in function

import pygame
from pygame.locals import * #imports useful pygame constants

import sys
from random import *

from vector import *

pygame.init()
#initializes pygame display so that Surfaces can be used
screen = pygame.display.set_mode((500,500),pygame.RESIZABLE)
#Constant for the distances between squares in the visualisation of tree
BETWEENLENGTH = 36

#creates a square at a given position that can be drawn to the screen
class Node:
    #the colour of the square does not have to be entered and is by default white
    def __init__(self,center,colour=(255,255,255),boxlength=30):
        self.BETWEENLENGTH = BETWEENLENGTH
        self.boxlength = boxlength #the value for the dimensions of both x and y of a box

        #creates a Surface for the square using the colour passed into the class
        self.image = pygame.Surface((self.boxlength,self.boxlength))
        self.image.fill(colour)
        #puts the Surface at the center of the position given
        self.rect = self.image.get_rect()
        self.rect.center = center
    def update(self,surf):
        #draws the square to the given surface
        surf.blit(self.image,self.rect)

#recursive function that returns the directions from the root of a tree to a node
def getdirections(nodekey,tree,last=0):
    #get the contents of the node from the tree dictionary
    node = tree[nodekey]
    #if the node is the root of the tree, then return an empty list
    try:
        if node[0] == "start" or nodekey == "A":
            return []
    except:
        return []
    else:
        directionlist = getdirections(node[0],tree)
        #adds the direction of the node to the direction list of the previous stack
        directionlist.append(node[1])
        #if the recursive function is at its original stack
        if last==1:
            #for every direction, reverse its orientation(e.g.: "w"="e", "n"="s")
            directions = ["n","e","s","w"]
            shiftdirect = ["s","w","n","e"]
            newlist = []
            for direction in directionlist:
                newlist.append(shiftdirect[directions.index(direction)])
            #reverse the list
            newlist.reverse()
            return newlist
        return directionlist

#returns a coordinate dictionary, where each key has coordinates relative to where the root of the tree is in units
def generatecoorddict(tree):
    newdict = {}
    #for every node
    for key in tree:
        #start coordinates at the root
        coords = [0,0]
        #get the directions to the a node from the root
        directionlist = getdirections(key,tree,1)
        #get relative unit coordinates by looping through and changing the coordinates based on the directions
        for direction in directionlist:
            if direction == "n":
                coords[1] -= 1
            elif direction == "s":
                coords[1] += 1
            elif direction == "e":
                coords[0] += 1
            elif direction == "w":
                coords[0] -= 1
        #put the node and coordinate into the new dictionary
        newdict[key] = coords
    #return the coordinate dictionary
    return newdict

#returns a list for the amount of rooms that should be from each direction from the root
def generatenumofrooms(num):
    #raise error if parameter is not divisible by 4
    if num%4 != 0:
        raise Exception ("number of total rooms not divisible by 4")
    # there will be 4 rooms already around the spawn, so there need to be 4 less
    num -= 4
    #the average amount of rooms for each direction
    average = num/4
    numlist = []
    for x in range(3):
        #generate a random proportion from the average amount of rooms for each direction
        randomint = int(average*uniform(0.2,1.5))
        #add that new room amount to list
        numlist.append(randomint)
    #find the remaining rooms that can be on the last side
    numlist.append(num-sum(numlist))
    return numlist

#generates a list of alphabet string combinations for tree names
def generatetreenames(num):
    possiblechars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars = []
    for char in possiblechars:
        chars.append(char)
    combinations = []
    
    #adds all single letters into the combinations
    for char1 in possiblechars:
        combinations.append(char1)
        
    #adds all double letter combinations
    for char1 in possiblechars:
        for char2 in possiblechars:
            string = char1 + char2
            combinations.append(string)
            
    #if the number of names needed is bigger than what is in the character list, raise error
    if num > len(combinations):
        raise Exception ("number of rooms too big")
    return combinations[0:num+10]#returns a cut down version of the name list


#from a node, returns a list of the directions to where nodes adjacent to it are
def getconnected(tree,targetkey):
    #check that the given target node is actually in the tree given
    connected = {}
    try:
        target = tree[targetkey]
        
    #raises exception if target node is not in tree
    except:
        raise Exception ("invalid key entered")

    #iterate through every node
    for key in tree:
        #if the node is not target node or the root node
        if key != "A" and tree[key] != tree[targetkey]:
            #if the node is connected to the target node
            if tree[key][0] == targetkey:
                #reverse the direction it contains, and add it to a dictionary of nodes connected to target node
                directions = ["n","e","s","w"]
                shiftdirect = ["s","w","n","e"]
                newdirection = tree[key][1]
                connected[key] = shiftdirect[directions.index(newdirection)]
    #put all the node names into a list
    directionlist = []
    for key in connected:
        direction = connected[key]
        directionlist.append(direction)
    if targetkey != "A":
        directionlist.append(tree[targetkey][1])
    return directionlist

#returns a dictionary of all the nodes with their data that are connected to the target node
def getconnected2(tree,targetkey):
    connected = {}
    try:
        target = tree[targetkey]
        
    #raises exception if target node is not in tree
    except:
        raise Exception ("invalid key entered")

    #iterate through every node
    for key in tree:
        #if the node is not target node or the root node
        if key != "A" and tree[key] != tree[targetkey]:
            #if the node is connected to the target node
            if tree[key][0] == targetkey:
                #put node contents into new dictionary
                connected[key] = tree[key]

    #if the node is not the root, add the node stored in its self
    if tree[targetkey] != []:
        selfkey = tree[targetkey][0]
        connected[selfkey] = tree[selfkey]
    return connected

#returns a dictionary of all nodes with their direction from the target node
def getconnected3(tree,targetkey):
    connected = {}
    try:
        target = tree[targetkey]
        
    #raises exception if target node is not in tree
    except:
        raise Exception ("invalid key entered")

    #iterate through every node
    for key in tree:
        #if the node is not target node or the root node
        if key != "A" and tree[key] != tree[targetkey]:
            #if the node is connected to the target node
            if tree[key][0] == targetkey:
                #put node contents into new dictionary
                directions = ["n","e","s","w"]
                shiftdirect = ["s","w","n","e"]
                newdirection = tree[key][1]
                connected[key] = shiftdirect[directions.index(newdirection)]
    #if the node is not the root, add the node stored in its self
    if tree[targetkey] != []:
        selfkey = tree[targetkey][0]
        connected[selfkey] = tree[targetkey][1]
    return connected


#get all the non dead end and dead end nodes in the tree
def getdeadends(tree):
    deadends = tree
    deadendkeys = []
    notdeadendkeys = []
    #put the names of each node into 2 lists
    for key in deadends:
        deadendkeys.append(key)
    

    #compares each node do each other
    for key1 in tree:
        node1 = tree[key1]
        for key2 in tree:
            #if the key being compared is not itself
            if key1 != key2:
                #if the node is not the root
                if key1 != "A":
                    #remove the node from a deadends if it has not been removed and has a connection to another node
                    if key2 in deadendkeys and node1[0] == key2:
                        notdeadendkeys.append(key2)
                        deadendkeys.remove(key2)
    #the list notdeadendkeys now contains the names of all non dead ends
    #the list deadendkeys contains all node names
                        
    #adds all nodes to deadendkeys that are not in notdeadendkeys
    """
    for item in tree:
        if item not in notdeadendkeys:
            deadendkeys.append(item)
    """
    #print(deadendkeys,notdeadendkeys)
    return deadendkeys,notdeadendkeys

#returns a LIST of the node names that are overlapping
def getoverlapping2(tree):
    overlaplist = []
    notoverlap = []
    #gets dictionary with the coordinates for each node relative to root node
    coords = generatecoorddict(tree)
    #iterate through nodes in the coordinate dictionary
    for key1 in coords:
        #if there is a duplicate node, its coordinates will already have been appended to a list
        if coords[key1] not in notoverlap:
            notoverlap.append(coords[key1])
        #if the node is a duplicate, add to a list
        else:
            overlaplist.append(key1)
    return overlaplist

#returns the NUMBER of overlapping nodes
def getoverlapping(tree):
    overlapcount = 0
    overlaplist = []
    #gets dictionary with the coordinates for each node relative to root node
    coords = generatecoorddict(tree)
    #iterate through nodes in the coordinate dictionary
    for key1 in coords:
        #if there is a duplicate node, its coordinates will already have been appended to a list
        if coords[key1] not in overlaplist:
            overlaplist.append(coords[key1])
        #if the node is a duplicate, add to the counter
        else:
            overlapcount +=1
    return overlapcount

#adds a node onto a tree
def addroom(newtree,keyname):
    #get a list of both the dead ends and non dead ends
    
    deadends,notdeadends = getdeadends(newtree)
    #generates a float between 1 and 0
    probability = uniform(0,1)
    #if the length of a branch is less than 2 or the probability
    #is bigger than 0.7
    if (probability > 0.7 or len(newtree)<=2):
        #pick a random dead end
        deadend = deadends[randint(0,len(deadends)-1)]
        #generates a float between 1 and 0
        probability = uniform(0,1)
        if probability > 0.7:
            #add a new node onto a dead end, in the same direction as it
            newtree[keyname] = [deadend,newtree[deadend][1]]
        else:
            #add a new node onto a dead end in a different direction to it
            direction = newtree[deadend][1]
            if direction == "n" or direction == "s":
                chance = ["e","w"]
                shuffle(chance)
                newdirection = chance[0]
            elif direction == "e" or direction == "w":
                chance = ["n","s"]
                shuffle(chance)
                newdirection = chance[0]
            newtree[keyname] = [deadend,newdirection] 
    else:
        #get a random non dead end
        notdeadend = notdeadends[randint(0,len(notdeadends)-1)]
        #get all the directions the not dead end is connected from
        notdirection = getconnected(newtree,notdeadend)
        directions = ["n","e","s","w"]
        for x in notdirection:
            try:
                directions.remove(x)
            except:
                pass
        #if there is a space around the not dead end, add a room to the side of it
        if directions != []:
            newdirection = directions[randint(0,len(directions)-1)]
            newkey = keyname
            newtree[newkey] = [notdeadend,newdirection]
        #if there is not a space, return nothing
        else:
            return None
    return newtree
                
def generatetree(numofrooms):
    #get list of alphabetical tree names
    treenames = generatetreenames(numofrooms)

    #define tree and add root node
    root = treenames.pop(0)
    tree = {
        root:[]
        }
    
    directions = ["n","e","s","w"]
    
    #add one node to each side of the root
    roomsfromspawn = []
    for direction in directions:
        name = treenames.pop(0)
        tree[name] = [root,direction]
        roomsfromspawn.append(name)
    #get the amount of rooms for each side from the spawn   
    roomnums = generatenumofrooms(numofrooms)

    #for each direction from spawn
    for num in range(4):
        #get one of the four rooms connected to the spawn
        startroom = roomsfromspawn[num]
        startnode = tree[startroom]
        roomnum = roomnums[num]

        #create tree which is used for a direction from spawn
        newtree = {startroom:startnode}
        #iterate through the number of rooms for a side from spawn
        while roomnum > 0:
            #put a new room onto the tree, with a new name
            toadd = addroom(newtree,treenames.pop(0))
            #if the algorithm tried to branch but failed do not change the tree
            if toadd == None:
                roomnum += 1
            #allow the change to take place if the room was placed successfully
            else:
                newtree = toadd
            roomnum -= 1
        #once all the new rooms have been added, add the new rooms to the actual tree
        for key in newtree:
            tree[key] = newtree[key]

    #get a list of overlapping nodes
    overlapping = getoverlapping2(tree)
    #while there are still overlapping nodes
    while overlapping != []:
        #re-add overlapping nodes onto the tree
        for key in overlapping:
            tree.pop(key)
            newtree = addroom(tree,key)
            while newtree == None:
                newtree = addroom(tree,key)
            tree = newtree
        #get a list of overlapping nodes
        overlapping = getoverlapping2(tree)
    
    return tree

def getunexplored(tree,exploredlist):
    adjacentexplore = []
    for key in exploredlist:
        adjacent = getconnected2(tree,key)
        for key in adjacent:
            if key not in exploredlist:
                adjacentexplore.append(key)
    return adjacentexplore

def getexploredtree(tree,exploredlist):
    adjacentexplore = getunexplored(tree,exploredlist)
    newtree = {}
    for key in adjacentexplore:
        newtree[key] = tree[key]
    for key in exploredlist:
        newtree[key] = tree[key]
    return newtree

def getnotincluded(tree,exploredlist):
    adjacent = getunexplored(tree,exploredlist)
    notinclude = []
    for key in tree:
        if key not in adjacent and key not in exploredlist:
            notinclude.append(key)
    return notinclude
    
#returns a modfied surface with the tree visualization on it
def generatemapsurface(tree,surf,keyshade=[],scale=None,notinclude=[],currentroom=None):
    #get the center of the surface to put the map on
    center = vector(surf.get_rect().size)/2
    nodestoadd = []
    coorddict = generatecoorddict(tree)
    #deadends,notdeadends = getdeadends(tree)
    length = BETWEENLENGTH
    if scale:
        length = surf.get_width()
        length = int((length)/13)
    #for every node in the tree
    for key in tree:
        center = vector(center)
        point1 = vector(coorddict[key])*length
        point1 += center
        #if the node is not the root
        if key != "A" and not key in notinclude and not tree[key][0] in notinclude:
            #draw a line between a node and the node it is connected to
            point2 = vector(coorddict[tree[key][0]])*length
            point2 += center
            colour = (255,255,255)
            if key in keyshade and tree[key][0] in keyshade:
                colour = (100,100,100)
            pygame.draw.line(surf,colour,point1,point2,length//5)
        #create node object at scaled coordinates
        if key in keyshade or not key in notinclude:
            nodecolour = (255,255,255)
            if key in keyshade:
                nodecolour = (100,100,100)
            if key == currentroom:
                nodecolour = (100,255,100)
            if scale:
                length2 = int(length*0.8)
                nodestoadd.append(Node(point1,nodecolour,length2))
            else:
                nodestoadd.append(Node(point1,nodecolour))
    #draw the nodes to the surface
    for node in nodestoadd:
        node.update(surf)
    return surf

def mapsurfacemultiplier(surf):
    length = surf.get_width()
    length = int((length)/13)
    return length

#generate a tree and draw it to a surface, as well as
#other options through key word arguments
def gettree(screen,**kwargs):
    roomnum = 12
    tree = generatetree(roomnum)
    deadends,notdeadends = getdeadends(tree)
    generatemapsurface(tree,screen)
    pygame.display.flip()
    for key in kwargs:
        #if there is the argument "output", save the surface generated to the path "output"
        #with a filename given as a key word argument
        if key == "output":
            pygame.image.save(screen,"output/"+kwargs["filename"]+".png")
        #if there is the argument "print", output the number of dead ends, number of rooms and overlapping rooms
        if key == "print":
            print("deadends:",len(deadends))
            print("number of rooms:",len(tree))
            print("overlaps:",getoverlapping(tree))
    return screen

        
        
            
