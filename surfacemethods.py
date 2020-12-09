import pygame
from pygame.locals import *

from vector import *

#returns image outline (not outlined image)
def outline(image):
    
    poss = [[0,1],[1,0],[2,1],[1,2],[1,1]]
    mask = pygame.mask.from_surface(image)
    #create blank image with alpha 0 (transparent)
    newimage = pygame.Surface(vector(image.get_size())+vector(2,2),pygame.SRCALPHA)
    newimage.fill((0,0,0,0))
    #use a mask to get the positions for the outline of an image
    #outlining a mask only gives the inside pixels and gives coordinates, not another mask
    outlinelist = mask.outline()
    outlinemask = pygame.Mask(image.get_size())
    #create an outline mask out of the outline coordinates
    for coord in outlinelist:
        outlinemask.set_at(coord,1)
    #turn the outline mask into a surface
    surf = outlinemask.to_surface(unsetcolor=(0,0,0,0),setcolor=(0,0,0,255))
    #blits the mask one pixel from the original picture's center for every cardinal direction
    #this is done because the current outline is only on the inside of the image
    for pos in poss:
        newimage.blit(surf,pos)
    return newimage

#returns a list of images from a spritesheet given the number of frames in that one spritesheet
#only works for spritesheets with images going horizontally and that all have the same width & height
def spritesheettolist(spritesheet,framenum,fulloutline=False,dooutline=True):
    #create blank list to store surfaces
    imagelist = []
    #works out the width of each frame in the spritesheet
    xtravel = spritesheet.get_width()//framenum
    #loops through the x positions for the top right of each frame int the spritesheet
    for x in range(0,spritesheet.get_width()+1-xtravel,xtravel):
        #create new transparent surface(alpha 0)
        newsurf = pygame.Surface(vector(xtravel,spritesheet.get_height()),pygame.SRCALPHA)
        newsurf.fill((0,0,0,0))
        #blit the image from the spritesheet onto the transparent image
        newsurf.blit(spritesheet,(-x,0))
        #get the surface for an outline
        outlinesurf = outline(newsurf)
        #there is a parameter for if the bottom part of the outline should be cut off
        #this is because if there is a sprite on the ground,the extra outline on the bottom
        #will make the sprite look like it is floating one pixel on the ground
        if not fulloutline:
            extra = vector(2,1)
        else:
            extra = vector(2,2)
        #apply the outline to the frame that has just been retrieved from the spritesheet
        newsurf2 = pygame.Surface(vector(xtravel,spritesheet.get_height())+extra,pygame.SRCALPHA)
        newsurf2.fill((0,0,0,0))
        newsurf2.blit(outlinesurf,(0,0))
        newsurf2.blit(newsurf,(1,1))
        #appends an outlined or non outlined image to the list of images
        if dooutline:
            imagelist.append(newsurf2)
        else:
            imagelist.append(newsurf)
    return imagelist
