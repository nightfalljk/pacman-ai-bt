import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from behaviortree import *

class Pacman(Entity):
    def __init__(self, node):
        Entity.__init__(self, node)
        self.name = PACMAN    
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        # self.sprites = PacmanSprites(self)
        self.btData = None
        self.directionMethod = self.goalDirection

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        # self.image = self.sprites.getStartImage()
        # self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP

    def update(self, dt):

        # Runs the behavior tree to determine a course of action
        self.bt()
        # self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt
        if self.overshotTarget():
            self.node = self.target
            directions = self.validDirections()
            direction = self.directionMethod(directions)
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()


    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None    
    
    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

    def setBTData(self, pellet_group, ghosts, fruit, goal_offset):
        # Creates a data object with all data required for the behavior tree
        self.btData = BTData(self, pellet_group, ghosts, fruit, goal_offset)

    def bt(self):

        # Determines whether there are any ghosts within a certain range of Pacman
        ghostClose = GhostClose(self.btData.ghosts, self.btData.pacman, 3 * TILEWIDTH)

        # Sequence that has Pacman chase ghosts within a certain range if they are in their FRIGHT state
        ghostScared = GhostScared(self.btData.ghosts, self.btData.pacman, 3 * TILEWIDTH)
        chaseGhosts = ChaseGhost(self.btData.ghosts, self.btData.pacman)
        chaseSequence = Sequence([ghostScared, chaseGhosts])

        flee = Flee(self.btData.ghosts, self.btData.pacman, self.btData.goal_offset, 3 * TILEWIDTH)

        # Selector that has Pacman chase ghosts if appropriate and flee other-wise
        chaseOrFleeSelector = Selector([chaseSequence, flee])

        # Sequence that determines if any ghosts are close-by and if so engages in chase or flee behavior
        ghostCloseSequence = Sequence([ghostClose, chaseOrFleeSelector])

        eatPills = EatPills(self.btData.pelletGroup, self)

        # Selector that engages in appropriate behavior when ghosts are close and eats pellets otherwise
        ghostsOrEat = Selector([ghostCloseSequence, eatPills])

        # Runs the behavior tree
        ghostsOrEat.run()
