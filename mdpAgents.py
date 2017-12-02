from pacman import Directions
from game import Agent
import api
import random
import game
import util
import sys
from mapAgents import Grid


class MDPAgent(Agent):

    # The constructor. We don't use this to create the map because it
    # doesn't have access to state information.
    def __init__(self):
        print "Running init!"

    # This function is run when the agent is created, and it has access
    # to state information, so we use it to build a map for the agent.
    def registerInitialState(self, state):
         print "Running registerInitialState!"
         # Make a map of the right size
         self.makeMap(state)
         self.addWallsToMap(state)
         self.updateFoodInMap(state)
         #self.map.display()
         self.UtilityVal = [0, 0, 0, 0]
         self.lastmove = Directions.STOP
         self.i = 0

    # This is what gets run when the game ends.
    def final(self, state):
        print "Looks like I just died!"
        self.i = 0

    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height)
        self.utilmapP = Grid(width, height)
        self.utilmapN = Grid(width,height)

    # Functions to get the height and the width of the grid.
    #
    # We add one to the value returned by corners to switch from the
    # index (returned by corners) to the size of the grid (that damn
    # "start counting at zero" thing again).
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')

    # Create a map with a current picture of the food that exists.
    def updateFoodInMap(self, state):
        # First, make all grid elements that aren't walls blank.
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    self.map.setValue(i, j, ' ')
        food = api.food(state)
        for i in range(len(food)):
            self.map.setValue(food[i][0], food[i][1], '*')

    def updateGhostsInMap(self,state):
        ghosts = api.ghosts(state)
        #print ghosts
        for i in range(len(ghosts)):
            self.map.setValue(int(ghosts[i][0]), int(ghosts[i][1]), '!')

    #Set reward value for a space depending on what it contains
    def RewardConversion(self,Mapvalue):
        #print Mapvalue
        if Mapvalue == '*':
            return 50
        elif Mapvalue == " ":
            return -0.5
        elif Mapvalue == '%':
            return 0
        elif Mapvalue == '!':
            return -100

    def InitUP(self):
        for i in xrange(self.map.getWidth()-1):
            for j in xrange(self.map.getHeight()-1):
                 R = self.RewardConversion(self.map.getValue(i,j))
                 self.utilmapP.setValue(i, j, R)

    def getAction(self, state):
        #Initialise legal moves, food and ghost position
        legal = api.legalActions(state)
        self.updateFoodInMap(state)
        self.updateGhostsInMap(state)
        if self.i == 0:
            self.InitUP()
            self.i = 1
        # Calculate utility values for map over a fixed amount of iterations to ensure convergence
        for count in xrange(5):
            for i in xrange(self.map.getWidth()-1):
                for j in xrange(self.map.getHeight()-1):
                    Current_util = self.utilmapP.getValue(i,j)
                    R = self.RewardConversion(self.map.getValue(i,j))
                    #Ignore walls
                    if R == 0:
                      continue
                    if Directions.NORTH not in legal:
                       up = Current_util
                    if Directions.SOUTH not in legal:
                        down = Current_util
                    if Directions.EAST not in legal:
                        left = Current_util
                    if Directions.WEST not in legal:
                        right = Current_util

                    # MAP origin is the bottom left
                    walls = api.walls(state)
                    up = self.utilmapP.getValue(i,j+1)
                    down = self.utilmapP.getValue(i,j-1)
                    left = self.utilmapP.getValue(i-1,j)
                    right = self.utilmapP.getValue(i+1,j)
                    Gamma = 0.6

                    Bellman = R + (Gamma* max(0.8*up+0.1*left+0.1*right, \
                    0.8*down + 0.1*left + 0.1*right, \
                    0.8*left + 0.1*up + 0.1*down, \
                    0.8*right + 0.1*up + 0.1*down))
                    self.utilmapN.setValue(i, j, round(Bellman,6))

            self.utilmapP = self.utilmapN

        # --------------------------------------------------------------------
        #Remove Stop if in legal actiona
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        pacman = api.whereAmI(state)
        #Obtain surrounding spaces
        self.UtilityVal[0] = [self.utilmapP.getValue(pacman[0],pacman[1]+1), Directions.NORTH]
        self.UtilityVal[1] = [self.utilmapP.getValue(pacman[0],pacman[1]-1), Directions.SOUTH]
        self.UtilityVal[2] = [self.utilmapP.getValue(pacman[0]-1,pacman[1]), Directions.WEST]
        self.UtilityVal[3] = [self.utilmapP.getValue(pacman[0]+1,pacman[1]), Directions.EAST]

        #Sort surrounding utilities to find maximum
        UT_sorted = sorted(self.UtilityVal)

        for i in xrange(len(UT_sorted)):
            UT = UT_sorted[len(UT_sorted) - 1 - i][1]
            if UT in legal:
                return api.makeMove(UT,legal)
