import pygame
pygame.init()
#abstraction for the pygame.math.Vector2() class so it is easier to create
#it returns a pygame vector object by taking in a tuple or two numbers
def vector(*overflow):
    #if there are two arguments
    if len(overflow) == 2:
        return pygame.math.Vector2(overflow[0],overflow[1])
    #if there is a singular tuple argument
    elif len(overflow) == 1:
        return pygame.math.Vector2(overflow[0])
    #raise error if parameters are not entered correctly
    else:
        raise Exception ("not a valid vector(tuple or 2 float)")

#short for linear interpolation, returns an amount between two values based off
#a percentage
def lerp(p1,p2,perc):
    return (perc * p1) + ((1-perc) * p2)

#Timer class so that events can be activated after a certain amount of frames
class Timer:
    #capacity of timer entered in initialization
    def __init__(self,maxtimer):
        self.maxtimer = maxtimer
        self.currentimer = 0
    #the current value of the actual incrementing timer is reset
    def reset(self):
        self.currentimer = 0
    #the timer is incremented and returns a bool based on if the timer has finished
    def update(self):
        self.currentimer += 1
        if self.currentimer >= self.maxtimer:
            return True
        return False
    def changemax(self,maxt):
        self.maxtimer = maxt

def inttuple(tuple1):
    newtuple = []
    for x in tuple1:
        newtuple.append(int(x))
    return tuple(newtuple)
