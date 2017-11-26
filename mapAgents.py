# mapAgents.py
# parsons/11-nov-2017
#
# Version 1.0
#
# A simple map-building to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is an extension of the above code written by Simon
# Parsons, based on the code in pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util
import sys

#
# A class that creates a grid that can be used as a map
#
# The map itself is implemented as a nested list, and the interface
# allows it to be accessed by specifying x, y locations.
#
class Grid:

    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # Print the grid out.
    def display(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # A new line after each line of the grid
            print
        # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],
            # A new line after each line of the grid
            print
        # A line after the grid
        print

    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

#
# An agent that creates a map.
#
# As currently implemented, the map places a % for each section of
# wall, a * where there is food, and a space character otherwise. That
# makes the display look nice. Other values will probably work better
# for decision making.
#

class MapAgent(Agent):

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
         self.map.display()
         self.UtilityVal = [0, 0, 0, 0]
         self.RewardVal = 0

    # This is what gets run when the game ends.
    def final(self, state):
        print "Looks like I just died!"

    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        print corners
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

    # Functions to manipulate the map.
    #
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
        print ghosts
        for i in range(len(ghosts)):
            self.map.setValue(int(ghosts[i][0]), int(ghosts[i][1]), '!')

    def RewardConversion(self,Mapvalue):
        print Mapvalue
        if Mapvalue == '*':
            self.RewardVal = int(10)
            return int(10)
        elif Mapvalue == " ":
            self.RewardVal = int(5)
            return int(5)
        elif Mapvalue == '%':
            self.RewardVal = int(0)
            return int(0)
        elif Mapvalue == '!':
            self.RewardVal = int(-100)
            return int -100


    def UtilityCalc(self,legal):
        for i in xrange(self.map.getWidth()-1):
            for j in xrange(self.map.getHeight()-1):
                Current_util = self.utilmapP.getValue(i,j)
                R = self.RewardConversion(self.map.getValue(i,j))
                up = self.utilmapP.getValue(i,j-1)
                down = self.utilmapP.getValue(i,j+1)
                left = self.utilmapP.getValue(i-1,j)
                right = self.utilmapP.getValue(i+1,j)
                Gamma = 0.2

                if Directions.NORTH not in legal:
                    up = Current_util
                if Directions.SOUTH not in legal:
                    down = Current_util
                if Directions.EAST not in legal:
                    left = Current_util
                if Directions.WEST not in legal:
                    right = Current_util

                Bellman = R + Gamma* max(0.8*up+0.1*left+0.1*right, \
                0.8*down + 0.1*left + 0.1*right, \
                0.8*left + 0.1*up + 0.1*down, \
                0.8*right + 0.1*up + 0.1*down)

                self.utilmapN.setValue(i, j, Bellman)

        self.utilmapP = self.utilmapN
        return self.utilmapP


    # For now I just move randomly, but I display the map to show my progress
    def getAction(self, state):

        legal = api.legalActions(state)
        self.updateFoodInMap(state)
        self.updateGhostsInMap(state)
        self.map.prettyDisplay()
        self.UtilityCalc(legal)
        print 'P:'
        self.utilmapP.prettyDisplay()
        print 'N:'
        self.utilmapN.prettyDisplay()

        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        print legal

        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        # Need to add in my MEU code here and change the values assigned to the map from star and spaces to values
        pacman = api.whereAmI(state)

        #down
        self.UtilityVal[0] = self.utilmapN.getValue(pacman[0],pacman[1]+1)
        #up
        self.UtilityVal[1] = self.utilmapN.getValue(pacman[0],pacman[1]-1)
        #right
        self.UtilityVal[2] = self.utilmapN.getValue(pacman[0]+1,pacman[1])
        #left
        self.UtilityVal[3] = self.utilmapN.getValue(pacman[0]-1,pacman[1])


        UT_sorted = sorted(self.UtilityVal)

        for i in xrange(length(UT_sorted)):
            UT = UT_sorted[length(UT_sorted) - i]

            if UT == self.UtilityVal[0]:
                if Directions.South in legal:
                    return api.makeMove(Directions.SOUTH,legal)
            if UT == self.UtilityVal[1]:
                if Directions.NORTH in legal:
                    return api.makeMove(Directions.NORTH,legal)
            if UT == self.UtilityVal[2]:
                if Directions.EAST in legal:
                    return api.makeMove(Directions.EAST,legal)
            if UT == self.UtilityVal[3]:
                if Directions.WEST in legal:
                    return api.makeMove(Directions.WEST,legal)






        # print pacMapValN
        # print pacMapValS
        # print pacMapValE
        # print pacMapValW
        #
        # MeuN = (0.8 * pacMapValN) + (0.1 * pacMapValE) + (0.1 * pacMapValW)
        # MeuS = (0.8 * pacMapValS) + (0.1 * pacMapValE) + (0.1 * pacMapValW)
        # MeuE = (0.8 * pacMapValE) + (0.1 * pacMapValN) + (0.1 * pacMapValS)
        # MeuW = (0.8 * pacMapValW) + (0.1 * pacMapValN) + (0.1 * pacMapValS)

        # if Directions.NORTH in legal:
        #     if self.UtilityVal[0] >= max(self.UtilityVal[1], self.UtilityVal[2], self.UtilityVal[3]):
        #         return api.makeMove(Directions.NORTH, legal)
        #
        # if Directions.SOUTH in legal:
        #     if self.UtilityVal[1] >= max(self.UtilityVal[0], self.UtilityVal[2], self.UtilityVal[3]):
        #         return api.makeMove(Directions.SOUTH, legal)
        #
        # if Directions.EAST in legal:
        #     if self.UtilityVal[2] >= max(self.UtilityVal[0], self.UtilityVal[1], self.UtilityVal[3]):
        #         return api.makeMove(Directions.EAST, legal)
        #
        # if Directions.WEST in legal:
        #     if self.UtilityVal[3] >= max(self.UtilityVal[0], self.UtilityVal[1], self.UtilityVal[2]):
        #         return api.makeMove(Directions.WEST, legal)
        #
        # # if Directions.NORTH in legal:
        #     if MeuN >= max(MeuS, MeuE, MeuW):
        #         MaxVal = MeuN
        # if Directions.SOUTH in legal:
        #     if MeuS >= max(MeuN, MeuE, MeuW):
        #         MaxVal = MeuS
        # if Directions.EAST in legal:
        #     if MeuE >= max(MeuS, MeuN, MeuW):
        #         MaxVal = MeuE
        # if Directions.WEST in legal:
        #     if MeuW >= max(MeuS, MeuE, MeuN):
        #         MaxVal = MeuW

        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)
