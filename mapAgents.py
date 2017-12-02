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
         #self.map.display()
         self.UtilityVal = [0, 0, 0, 0]
         self.lastmove = Directions.STOP
         self.llastmove = Directions.STOP
         self.i = 0
    # This is what gets run when the game ends.
    def final(self, state):
        print "Looks like I just died!"

    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        #print corners
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height)
        self.utilmapP = Grid(width, height)
        self.InitUP()
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
        #print ghosts
        for i in range(len(ghosts)):
            self.map.setValue(int(ghosts[i][0]), int(ghosts[i][1]), '!')

    def RewardConversion(self,Mapvalue):
        #print Mapvalue
        if Mapvalue == '*':
            return 50
        elif Mapvalue == " ":
            return 1
        elif Mapvalue == '%':
            return 0
        elif Mapvalue == '!':
            return -100

    def InitUP(self):
        for i in xrange(self.map.getWidth()-1):
            for j in xrange(self.map.getHeight()-1):
                R = self.RewardConversion(self.map.getValue(i,j))
                self.utilmapP.setValue(i, j, R)


    # def UtilityCalc(self,legal):
    #     print 'initial'
    #     print self.s1
    #     print self.s2
    #     while abs(self.diff) > 10:
    #         for i in xrange(self.map.getHeight()-1):
    #             for j in xrange(self.map.getWidth()-1):
    #                 Current_util = self.utilmapP.getValue(i,j)
    #                 R = self.RewardConversion(self.map.getValue(i,j))
    #                 up = self.utilmapP.getValue(i-1,j)
    #                 down = self.utilmapP.getValue(i+1,j)
    #                 left = self.utilmapP.getValue(i,j-1)
    #                 right = self.utilmapP.getValue(i,j+1)
    #                 Gamma = 0.2
    #
    #                 if Directions.NORTH not in legal:
    #                     up = Current_util
    #                 if Directions.SOUTH not in legal:
    #                     down = Current_util
    #                 if Directions.EAST not in legal:
    #                     left = Current_util
    #                 if Directions.WEST not in legal:
    #                     right = Current_util
    #
    #                 Bellman = R + Gamma* max(0.8*up+0.1*left+0.1*right, \
    #                 0.8*down + 0.1*left + 0.1*right, \
    #                 0.8*left + 0.1*up + 0.1*down, \
    #                 0.8*right + 0.1*up + 0.1*down)
    #
    #                 self.s1 = self.s1 + Bellman
    #                 self.utilmapN.setValue(i, j, Bellman)
    #             print 'for loop'
    #             print self.s1
    #             print self.utilmapN
    #
    #         self.diff = self.s2 - self.s1
    #         print 'while loop'
    #         print abs(self.diff)
    #         print 's2', self.s2
    #         print 's1', self.s1
    #         #reset prev s2 to new s1
    #         self.s2 = self.s1
    #         self.utilmapP = self.utilmapN
    #     print 'reset'
    #     print self.s2
    #     print self.s1



    # For now I just move randomly, but I display the map to show my progress
    def getAction(self, state):

        legal = api.legalActions(state)
        self.updateFoodInMap(state)
        self.updateGhostsInMap(state)
        #self.map.prettyDisplay()
        if self.i == 0:
            self.InitUP()
            self.i = 1

        #self.utilmapP.prettyDisplay()
        # ---------------------------------------------------------------------
        #print 'initial'

        count = 1
        for count in xrange(20):
            for i in xrange(self.map.getWidth()-1):
                for j in xrange(self.map.getHeight()-1):
                    Current_util = self.utilmapP.getValue(i,j)
                    R = self.RewardConversion(self.map.getValue(i,j))
                    if R == 0:
                      continue
                    # MAP origin is the bottom left

                    walls = api.walls(state)
                    up = self.utilmapP.getValue(i,j+1)
                    down = self.utilmapP.getValue(i,j-1)
                    left = self.utilmapP.getValue(i-1,j)
                    right = self.utilmapP.getValue(i+1,j)

                    Gamma = 0.5
                    #print legal
                    #print up, down, left, right

                    # if Directions.NORTH not in legal:
                    #     up = Current_util
                    # if Directions.SOUTH not in legal:
                    #     down = Current_util
                    # if Directions.EAST not in legal:
                    #     left = Current_util
                    # if Directions.WEST not in legal:
                    #     right = Current_util
                    #print legal
                    #print up, down, left, right
                    #raw_input('')

                    Bellman = R + (Gamma* max(0.8*up+0.1*left+0.1*right, \
                    0.8*down + 0.1*left + 0.1*right, \
                    0.8*left + 0.1*up + 0.1*down, \
                    0.8*right + 0.1*up + 0.1*down))
                    #print 'Bellman',Bellman

                    self.utilmapN.setValue(i, j, round(Bellman,4))
                    #self.utilmapN.prettyDisplay()

                    #print 'P',self.utilmapP.getValue(i,j)
                    #print 'N',self.utilmapN.getValue(i,j)

                    #raw_input('')
            #self.utilmapP.prettyDisplay()
            #self.utilmapN.prettyDisplay()
            self.utilmapP = self.utilmapN
            #print 'update'



        # --------------------------------------------------------------------




        #print 'P:'
        #self.utilmapP.prettyDisplay()
        #print 'N:'
        #self.utilmapN.prettyDisplay()


        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        #print legal

        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        # Need to add in my MEU code here and change the values assigned to the map from star and spaces to values
        pacman = api.whereAmI(state)
        #UP
        self.UtilityVal[0] = [self.utilmapP.getValue(pacman[0],pacman[1]+1), Directions.NORTH]
        #DOWN
        self.UtilityVal[1] = [self.utilmapP.getValue(pacman[0],pacman[1]-1), Directions.SOUTH]
        #WEST
        self.UtilityVal[2] = [self.utilmapP.getValue(pacman[0]-1,pacman[1]), Directions.WEST]
        #EAST
        self.UtilityVal[3] = [self.utilmapP.getValue(pacman[0]+1,pacman[1]), Directions.EAST]

        self.llastmove = self.lastmove
        UT_sorted = sorted(self.UtilityVal)
        # print UT_sorted
        # if self.lastmove == UT_sorted[2][1]:
        #     a = UT_sorted[2]
        #     UT_sorted[2] = UT_sorted[3]
        #     UT_sorted[3] = a


        # print UT_sorted
        # print self.lastmove
        # print UT_sorted[3][1]
        #
        # print 'up down west east'
        # #raw_input('')

        for i in xrange(len(UT_sorted)):

            UT = UT_sorted[len(UT_sorted) - 1 - i]

            if UT == self.UtilityVal[0]:
                if Directions.NORTH in legal:
                    self.lastmove = Directions.NORTH
                    return api.makeMove(Directions.NORTH,legal)
            if UT == self.UtilityVal[1]:
                if Directions.SOUTH in legal:
                    self.lastmove = Directions.SOUTH
                    return api.makeMove(Directions.SOUTH,legal)
            if UT == self.UtilityVal[2]:
                if Directions.WEST in legal:
                    self.lastmove = Directions.WEST
                    return api.makeMove(Directions.WEST,legal)
            if UT == self.UtilityVal[3]:
                if Directions.EAST in legal:
                    self.lastmove = Directions.EAST
                    return api.makeMove(Directions.EAST,legal)

        # Random choice between the legal options.
        return api.makeMove(random.choice(legal), legal)
