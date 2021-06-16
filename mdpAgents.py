# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
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
import sys


class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)
        self.makeMap(state)
        self.addWallsToMap(state)
        self.updateFoodInMap(state)
        self.updateGhostInMap(state)
        self.map.display()

    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

     # Make a map by creating a grid of the right size
    def makeMap(self, state):
        corners = api.corners(state)
        print corners
        height = self.getLayoutHeight(corners)
        width = self.getLayoutWidth(corners)
        self.map = Grid(width, height)

        # Creating a utility grid and setting initial values to 0
        self.utilGrid = []
        for i in range(self.map.width):
            row = []
            for j in range(self.map.height):
                row.append(0)
            self.utilGrid.append(row)

        # Creating a copy of the utility grid and setting initial values to 0.
        self.utilCopy = []
        for i in range(self.map.width):
            row = []
            for j in range(self.map.height):
                row.append(0)
            self.utilCopy.append(row)

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

        # Update values for food located in the map and add to the utilGrid.
        food = api.food(state)
        for i in range(len(food)):
            self.utilGrid[food[i][0]][food[i][1]] = 25
            self.map.setValue(food[i][0], food[i][1], 'F')

    # Add the values of the ghosts to the map and add to the utilGrid.
    def updateGhostInMap(self, state):
        g = api.ghosts(state)
        for i in range(len(g)):
            self.utilGrid[int(g[i][0])][int(g[i][1])] = -50
            self.map.setValue(int(g[i][0]), int(g[i][1]), 'G')

            if int(g[i][0] + 1) != '%' and int(g[i][0] + 1) < self.map.getWidth():
                self.utilGrid[int(g[i][0] + 1)][int(g[i][1])] = -35
            elif int(g[i][0] - 1) != '%' and int(g[i][0] - 1) < self.map.getWidth():
                self.utilGrid[int(g[i][0] - 1)][int(g[i][1])] = -35
            elif int(g[i][1] + 1) != '%' and int(g[i][1] + 1) < self.map.getHeight():
                self.utilGrid[int(g[i][0])][int(g[i][1]) + 1] = -35
            elif int(g[i][1] - 1) != '%' and int(g[i][1] - 1) < self.map.getHeight():
                self.utilGrid[int(g[i][0])][int(g[i][1]) - 1] = -35

    # Add the values of the capsules to the map and add to the utilGrid (only needed in mediumClassic).
    def updateCapsulesInMap(self, state):
        c = api.capsules(state)
        for i in range(len(c)):
            self.utilGrid[int(c[i][0])][int(c[i][1])] = 25
            self.map.setValue(int(c[i][0]), int(c[i][1]), 'C')

    # Function finds all the legal actions, updates the food, ghosts and capsules in the map and returns and
    # executes the move direction stated from the bellman function.
    def getAction(self, state):
        legal = api.legalActions(state)
        self.updateFoodInMap(state)
        self.updateCapsulesInMap(state)
        self.updateGhostInMap(state)
        # Random choice between the legal options.
        return api.makeMove(self.bellman(state), legal)

    # Function to check if the move Pac-man wants to make is legal, if so, add it to the possible movements array.
    def checkLegal(self, i, j):
        possibleMovements = []
        currentPosX = i
        currentPosY = j
        if self.map.getValue(currentPosX, currentPosY + 1) != "%":
            possibleMovements.append("North")
        if self.map.getValue(currentPosX + 1, currentPosY) != "%":
            possibleMovements.append("East")
        if self.map.getValue(currentPosX, currentPosY - 1) != "%":
            possibleMovements.append("South")
        if self.map.getValue(currentPosX - 1, currentPosY) != "%":
            possibleMovements.append("West")
        return possibleMovements

    # Function to calculate the maximum utility in each direction next to Pac-man.
    def maxUtil(self, i, j):
        currentPosX = i
        currentPosY = j
        NorthUtil = self.utilGrid[currentPosX][currentPosY + 1]
        EastUtil = self.utilGrid[currentPosX + 1][currentPosY]
        WestUtil = self.utilGrid[currentPosX - 1][currentPosY]
        SouthUtil = self.utilGrid[currentPosX][currentPosY - 1]

        # Directions and directionUtil are organised in the same order so we can use the index of directions to know
        # which direction we're referring to when we calculate the maximum utility of all four directions.
        directions = ['North', 'South', 'East', 'West']
        directionUtil = [NorthUtil, SouthUtil, EastUtil, WestUtil]

        action = self.checkLegal(i, j)

        maxUtil = -10000
        for i in directions:
            if i in action:
                maxUtil = max(directionUtil[directions.index(i)], maxUtil)
        action = directionUtil.index(maxUtil)
        action = directions[action]
        return maxUtil

    # Bellman function that also computes the value iteration for Pac-man. The function first updates all the non-empty
    # spaces in the grid and then has a loop that runs for a set amount of iterations to update the utilities if the
    # coordinates do not have food, ghosts, capsules or walls. Function also determines which moves are possible from
    # the list of available directions and then calculates the utility of moving to that direction (North, South, East
    # and West). Based on the utilities, the bellman function calculates the maximum utility which signals where Pac-man
    # should do and then sends that information to the getAction function to carry out Pac-man's next move.
    def bellman(self, state):
        self.updateFoodInMap(state)
        self.updateCapsulesInMap(state)
        self.updateGhostInMap(state)

        # If condition to check the layout of the grid, if the height of the grid is 10 then we know we're dealing with
        # the mediumClassic map. During the testing of the program, better results were reached when the discount
        # factor was higher and when because the map is bigger than the small grid, the bellman equation needed more
        # loops to reach convergence and 275 worked well for this implementation.
        if Grid.getHeight(self.map) == 10:
            reward = -0.3
            discountFactor = 0.835
            for a in range(275):
                # Updating the values of utilGrid to match utilCopy
                self.utilGrid = self.utilCopy
                for i in range(self.map.getWidth()):
                    for j in range(self.map.getHeight()):
                        if self.map.getValue(i, j) != "%" and self.map.getValue(i, j) != 'G' and self.map.getValue(i,j)\
                                != 'F' and self.map.getValue(i, j) != 'C':
                            self.utilCopy[i][j] = reward + (discountFactor * self.maxUtil(i, j))

        # If the height of the Grid is not 10, then we know that the map is the smallGrid one so we use fewer iterations
        # of the loop since we can reach convergence quicker. This saves time because there's not a lot of space to
        # iterate for and so pacman can move faster here to try and avoid the ghost.
        else:
            discountFactor = 0.750
            reward = -0.3
            for a in range(130):
                # Updating the values of utilGrid to match utilCopy
                self.utilGrid = self.utilCopy
                for i in range(self.map.getWidth()):
                    for j in range(self.map.getHeight()):
                        if self.map.getValue(i, j) != "%" and self.map.getValue(i, j) != 'G' and self.map.getValue(i,j) != 'F' and self.map.getValue(i, j) != 'G1':
                            self.utilCopy[i][j] = reward + (discountFactor * self.maxUtil(i, j))

        # Finding the current (x,y) coordinates of Pacman.
        currentPos = api.whereAmI(state)
        currentPosX = currentPos[0]
        currentPosY = currentPos[1]

        # Checking which move in the four directions (North, South, East, West) is legal for Pacman.
        action = self.checkLegal(currentPosX, currentPosY)
        nextNorth = -1000
        nextSouth = -1000
        nextEast = -1000
        nextWest = -1000

        # This block of if else statements shows that if there is an available action,
        # pacman determines the utility of going in that direction but since the program
        # is non-deterministic, we need to account for moving in the other two directions as well if they are legal.
        # So this block of if else statements checks from the legal moves and calculates the total utility for the next
        # coordinate in the legal directions. If Pacman has North in its legal actions, we disregard going South and we
        # check if East and West are legal actions too, then we say that Pac-man has an 80% chance of moving north and
        # we divide the rest of the percentages to any other direction which is possible, if it can only move in 2
        # directions or fewer, we also add the utility of Pac-man staying in the same location.
        if "North" in action:
            if "West" in action and "East" in action:
                nextNorth = (self.utilGrid[currentPosX][currentPosY + 1] * 0.8) + (
                        self.utilGrid[currentPosX - 1][currentPosY] * 0.1) + (
                                    self.utilGrid[currentPosX + 1][currentPosY] * 0.1)
            elif "West" in action:
                nextNorth = (self.utilGrid[currentPosX][currentPosY + 1] * 0.8) + (
                        self.utilGrid[currentPosX - 1][currentPosY] * 0.1) + (
                                    self.utilGrid[currentPosX][currentPosY] * 0.1)
            elif "East" in action:
                nextNorth = (self.utilGrid[currentPosX][currentPosY + 1] * 0.8) + (
                        self.utilGrid[currentPosX + 1][currentPosY] * 0.1) + (
                                    self.utilGrid[currentPosX][currentPosY] * 0.1)
            else:
                nextNorth = (self.utilGrid[currentPosX][currentPosY + 1] * 0.8) + (
                        self.utilGrid[currentPosX][currentPosY] * 0.2)

        if "West" in action:
            if "North" in action and "South" in action:
                nextWest = (self.utilGrid[currentPosX - 1][currentPosY] * 0.8) + (
                        self.utilGrid[currentPosX][currentPosY + 1] * 0.1) + (
                                   self.utilGrid[currentPosX][currentPosY - 1] * 0.1)
            elif "North" in action:
                nextWest = (self.utilGrid[currentPosX - 1][currentPosY] * 0.8) + (
                        self.utilGrid[currentPosX][currentPosY + 1] * 0.1) + (
                                   self.utilGrid[currentPosX][currentPosY] * 0.1)
            elif "South" in action:
                nextWest = (self.utilGrid[currentPosX - 1][currentPosY] * 0.8) + (
                        self.utilGrid[currentPosX][currentPosY - 1] * 0.1) + (
                                   self.utilGrid[currentPosX][currentPosY] * 0.1)
            else:
                nextWest = (self.utilGrid[currentPosX - 1][currentPosY] * 0.8) + (
                        self.utilGrid[currentPosX][currentPosY] * 0.2)

        if "East" in action:
            if "North" in action and "South" in action:
                nextEast = (self.utilGrid[currentPosX + 1][currentPosY] * 0.8) + (
                        self.utilGrid[currentPosX][currentPosY + 1] * 0.1) + (
                                   self.utilGrid[currentPosX][currentPosY - 1] * 0.1)
            elif "North" in action:
                nextEast = (self.utilGrid[currentPosX + 1][currentPosY] * 0.8) + (
                        self.utilGrid[currentPosX][currentPosY + 1] * 0.1) + (
                                   self.utilGrid[currentPosX][currentPosY] * 0.1)
            elif "South" in action:
                nextEast = (self.utilGrid[currentPosX + 1][currentPosY] * 0.8) + (
                        self.utilGrid[currentPosX][currentPosY - 1] * 0.1) + (
                                   self.utilGrid[currentPosX][currentPosY] * 0.1)
            else:
                nextEast = (self.utilGrid[currentPosX + 1][currentPosY] * 0.8) + (
                        self.utilGrid[currentPosX][currentPosY] * 0.2)

        if "South" in action:
            if "West" in action and "East" in action:
                nextSouth = (self.utilGrid[currentPosX][currentPosY - 1] * 0.8) + (
                        self.utilGrid[currentPosX - 1][currentPosY] * 0.1) + (
                                    self.utilGrid[currentPosX + 1][currentPosY] * 0.1)
            elif "West" in action:
                nextSouth = (self.utilGrid[currentPosX][currentPosY - 1] * 0.8) + (
                        self.utilGrid[currentPosX - 1][currentPosY] * 0.1) + (
                                    self.utilGrid[currentPosX][currentPosY] * 0.1)
            elif "East" in action:
                nextSouth = (self.utilGrid[currentPosX][currentPosY - 1] * 0.8) + (
                        self.utilGrid[currentPosX + 1][currentPosY] * 0.1) + (
                                    self.utilGrid[currentPosX][currentPosY] * 0.1)
            else:
                nextSouth = (self.utilGrid[currentPosX][currentPosY - 1] * 0.8) + (
                        self.utilGrid[currentPosX][currentPosY] * 0.2)

        # Similar to the maxUtil function, this block of code checks the max of the legal directions out of the four
        # and assigns that value and direction to the action variable and returns finalMove which is send to the
        # getAction function to move Pac-man based on the MDP above.
        directions = ['North', 'South', 'East', 'West']
        directionUtil = [nextNorth, nextSouth, nextEast, nextWest]
        maxUtil = -10000
        for i in directions:
            if i in action:
                maxUtil = max(directionUtil[directions.index(i)], maxUtil)
        action = directionUtil.index(maxUtil)
        finalMove = directions[action]
        return finalMove


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
            row = []
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
