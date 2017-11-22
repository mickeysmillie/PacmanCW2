# partialAgent.py
# parsons/15-oct-2017
#
# Version 1
#
# The starting point for CW1.
#
# Intended to work with the PacMan AI projects from:
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

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

# partialAgent.py
# parsons/15-oct-2017
#
# Version 1
#
# The starting point for CW1.
#
# Intended to work with the PacMan AI projects from:
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

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util
from game import Actions


class PartialAgent(Agent):

        # Constructor: this gets run when we first invoke pacman.py
        def __init__(self):
            print "Pacman :  "
            name = "Pacman"
            self.last = Directions.STOP
            # Corner initialisation
            self.BL = False
            self.TL = False
            self.BR = False
            self.TR = False

        # This is what gets run in between multiple games
        def final(self, state):
            print "New Game: "
            #Variables are reset between games
            self.BL = False
            self.TL = False
            self.BR = False
            self.TR = False
            self.last = Directions.STOP

        # Function to calculate closest food/ghost to pacman
        def least_dist(self, pacman_loc, locs):
            # Setup variable to hold the values
            n = 0
            least_distance = 100
            # Determine closest location
            for i in xrange(len(locs)):
                dist = util.manhattanDistance(pacman_loc, locs[i])
                # Store the smallest distance and the index
                if dist < least_distance:
                    least_distance = dist
                    n = i
            return locs[n]

        # Function to calculate direction vector to food/ghost from pacman
        def vector_to_location(self, pacman_location, loc):
            # Difference between pacman and the location
            diff_x = loc[0] - pacman_location[0]
            diff_y = loc[1] - pacman_location[1]

            #Translate the differences in a direction vector
            if diff_x > 0:
                diff_x = 1
            elif diff_x < 0:
                diff_x = -1
            if diff_y > 0:
                diff_y = 1
            elif diff_y < 0:
                diff_y = -1

            dir_vec = [diff_x, diff_y]
            return dir_vec

        # Function to determine direction that pacman will move in
        def getAction(self, state):
            # Get the actions we can try, and remove "STOP" if that is one of them.
            legal = api.legalActions(state)
            if Directions.STOP in legal:
                legal.remove(Directions.STOP)

            # Get all information need from the api
            ghost_location = api.ghosts(state)
            pacman_location = api.whereAmI(state)
            food_location = api.food(state)
            walls_location = api.walls(state)
            corners_location = api.corners(state)
            print "Corners", corners_location
            print "walls", walls_location

            # ------- GHOSTS CODE --------

            # Ghosts are heard
            if ghost_location != []:
                # Find the closest ghost
                ghost = self.least_dist(pacman_location, ghost_location)
                # Direction of closest ghost
                bad_vector = self.vector_to_location(pacman_location, ghost)

                # if the ghost is an orthogonal direction -
                # Try to go in the opposite direction
                # If not possible remove the bad direction and then randomly choose
                if bad_vector[0] == 0 or bad_vector[1] == 0:
                    #Calculate the opposite direction to ghost direction
                    x = bad_vector[0] * -1
                    y = bad_vector[1] * -1
                    good_vector = [x, y]
                    good_move = Actions.vectorToDirection(good_vector)
                    bad_move = Actions.vectorToDirection(bad_vector)
                    if good_move in legal:
                        self.last = good_move
                        return api.makeMove(good_move,legal)
                    if bad_move in legal:
                        legal.remove(bad_move)
                    # If no legal moves, put Stop direction back into legal moves
                    if legal == []:
                        legal.append(Directions.STOP)
                    # Choose either the last move or pick a new one
                    if self.last in legal:
                        return api.makeMove(self.last,legal)
                    else:
                        pick = random.choice(legal)
                        return api.makeMove(pick, legal)

                # if ghost isn't in an orthogonal direction -
                # Split the vector into two bad moves and remove both from legal
                elif bad_vector[0] and bad_vector[1] != 0:
                    second_vector = [0,bad_vector[1]]
                    bad_move2 = Actions.vectorToDirection(second_vector)
                    bad_vector[1] = 0
                    bad_move = Actions.vectorToDirection(bad_vector)

                    if bad_move in legal:
                        legal.remove(bad_move)
                    if bad_move2 in legal:
                        legal.remove(bad_move2)
                    # If no legal moves, put Stop direction back into legal moves
                    if legal == []:
                        legal.append(Directions.STOP)
                    # Choose either the last move or pick a new one
                    if self.last in legal:
                        return api.makeMove(self.last, legal)
                    else:
                        pick = random.choice(legal)
                        return api.makeMove(pick, legal)

            # ------- FOOD CODE ----------
            # If no ghosts are detected, pacman will concetrate on food
            elif ghost_location == []:
                caps_location = api.capsules(state)
                # Add capsule location to food array if detected
                if caps_location != []:
                    food_location.append(caps_location[0])


                # If food isn't found then do corner agents
                if food_location == []:

                    # Get extreme x and y values for the grid
                    corners = api.corners(state)
                    # Setup variable to hold the values
                    minX = 100
                    minY = 100
                    maxX = 0
                    maxY = 0

                    # Sweep through corner coordinates looking for max and min
                    # values.
                    for i in range(len(corners)):
                        cornerX = corners[i][0]
                        cornerY = corners[i][1]

                        if cornerX < minX:
                            minX = cornerX
                        if cornerY < minY:
                            minY = cornerY
                        if cornerX > maxX:
                            maxX = cornerX
                        if cornerY > maxY:
                            maxY = cornerY

                    # ------------ BOTTOM LEFT -----------
                    # Check we aren't there:
                    if pacman_location[0] == minX + 1:
                        if pacman_location[1] == minY + 1:
                            self.BL = True

                    # If not, move towards it, first to the West, then to the South.
                    if self.BL == False:
                        if pacman_location[0] > minX + 1:
                            if Directions.WEST in legal:
                                return api.makeMove(Directions.WEST, legal)
                            else:
                                pick = random.choice(legal)
                                return api.makeMove(pick, legal)
                        else:
                            if Directions.SOUTH in legal:
                                return api.makeMove(Directions.SOUTH, legal)
                            else:
                                pick = random.choice(legal)
                                return api.makeMove(pick, legal)

                    # ------------ TOP LEFT -------------------

                    # Check we aren't there:
                    if pacman_location[0] == minX + 1:
                       if pacman_location[1] == maxY - 1:
                            self.TL = True

                    # If not, move West then North.
                    if self.TL == False:
                        if pacman_location[0] > minX + 1:
                            if Directions.WEST in legal:
                                return api.makeMove(Directions.WEST, legal)
                            else:
                                pick = random.choice(legal)
                                return api.makeMove(pick, legal)
                        else:
                            if Directions.NORTH in legal:
                                return api.makeMove(Directions.NORTH, legal)
                            else:
                                pick = random.choice(legal)
                                return api.makeMove(pick, legal)

                    # --------- TOP RIGHT --------------

                    # Check we aren't there:
                    if pacman_location[0] == maxX - 1:
                       if pacman_location[1] == maxY - 1:
                            self.TR = True

                    # Move east where possible, then North
                    if self.TR == False:
                        if pacman_location[0] < maxX - 1:
                            if Directions.EAST in legal:
                                return api.makeMove(Directions.EAST, legal)
                            else:
                                pick = random.choice(legal)
                                return api.makeMove(pick, legal)
                        else:
                            if Directions.NORTH in legal:
                                return api.makeMove(Directions.NORTH, legal)
                            else:
                                pick = random.choice(legal)
                                return api.makeMove(pick, legal)

                    # --------- BOTTOM RIGHT --------------

                    if pacman_location[0] == maxX - 1:
                       if pacman_location[1] == minY + 1:
                            self.BR = True

                    if self.BR == False:
                        if pacman_location[0] < minX - 1:
                            if Directions.EAST in legal:
                                return api.makeMove(Directions.EAST, legal)
                            else:
                                pick = random.choice(legal)
                                return api.makeMove(pick, legal)
                        else:
                            if Directions.SOUTH in legal:
                                return api.makeMove(Directions.SOUTH, legal)
                            else:
                                pick = random.choice(legal)
                                return api.makeMove(pick, legal)

                    if self.BR == True:
                        self.TL = False
                        self.TR = False
                        self.BL = False
                        self.BR = False

                    if self.last in legal:
                        return api.makeMove(self.last, legal)
                    else:
                        pick = random.choice(legal)
                        return api.makeMove(pick,legal)

                # Food is found:
                elif food_location != []:
                    # Find the closest food
                    food = self.least_dist(pacman_location, food_location)
                    # Find the direction of closest food
                    good_vec = self.vector_to_location(pacman_location,food)
                    # Translate vector to a move
                    move = Actions.vectorToDirection(good_vec)
                    if move in legal:
                        self.last = move
                        return api.makeMove(move,legal)
