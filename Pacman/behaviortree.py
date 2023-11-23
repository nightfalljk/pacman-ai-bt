from vector import Vector2
from constants import *
import math

class BTData(object):
    # Data structure storing all data required by the behavior tree
    def __init__(self, pacman, pellet_group, ghosts, fruit, goal_offset):
        self.pacman = pacman
        self.pelletGroup = pellet_group
        self.ghosts = ghosts
        self.fruit = fruit
        self.goal_offset = goal_offset

class Task(object):
    #  Basic Task class for Behavior Tree
    def run(self) -> bool:
        return False


class Selector(Task):
    #  Selector Node for Behavior Tree
    def __init__(self, children=[]):
        self.children = children

    def run(self) -> bool:
        for child in self.children:
            if child.run():
                return True
        return False


class Sequence(Task):
    #  Sequence Node for Behavior Tree
    def __init__(self, children=[]):
        self.children = children

    def run(self) -> bool:
        for child in self.children:
            if not child.run():
                return False
        return True


class GhostClose(Task):
    #  Determines whether any ghost is closer than a certain threshold towards Pacman
    def __init__(self, ghosts, pacman, dist_threshold):
        self.ghosts = ghosts
        self.pacman = pacman
        self.distThreshold = dist_threshold

    def run(self) -> bool:
        for ghost in self.ghosts:
            dist = (self.pacman.position - ghost.position).magnitude()
            if dist < self.distThreshold:
                return True

        return False

class GhostScared(Task):
    #  Determines whether the ghosts are in their FRIGHT state
    def __init__(self, ghosts, pacman,  dist_threshold):
        self.ghosts = ghosts
        self.pacman = pacman
        self.dist_threschold = dist_threshold

    def run(self) -> bool:
        closestDist = -1
        closestGhost = None
        for ghost in self.ghosts:
            dist = (self.pacman.position - ghost.position).magnitude()
            if closestGhost is None or dist < closestDist:
                closestGhost = ghost
                closestDist = dist

        if closestGhost.mode.current is FREIGHT:
            return True

        return False


class ChaseGhost(Task):
    #  Sets the closest ghost as goal for Pacman
    def __init__(self, ghosts, pacman):
        self.ghosts = ghosts
        self.pacman = pacman

    def run(self) -> bool:
        closestDist = -1
        closestGhost = None
        for ghost in self.ghosts:
            dist = (self.pacman.position - ghost.position).magnitude()
            if closestGhost is None or dist < closestDist and ghost.mode.current is FREIGHT:
                closestGhost = ghost
                closestDist = dist

        self.pacman.goal = closestGhost.position
        self.pacman.color = RED
        return True


class Flee(Task):
    # Calculates the average of all ghost direction vectors towards Pacman and sets an escape goal for Pacman based
    # on that
    def __init__(self, ghosts, pacman, goal_offset, dist_threshold):
        self.ghosts = ghosts
        self.pacman = pacman
        self.goal_offset = goal_offset
        self.distThreshold = dist_threshold

    def run(self) -> bool:
        acc_x = 0
        acc_y = 0
        num_close_ghosts = 0
        for ghost in self.ghosts:
            dir = self.pacman.position - ghost.position
            if dir.magnitude() < self.distThreshold:
                acc_x += dir.x
                acc_y += dir.y
                num_close_ghosts += 1
        avg_dir = Vector2(math.floor(acc_x/num_close_ghosts), math.floor(acc_y/num_close_ghosts))

        self.pacman.goal = self.pacman.position + avg_dir * self.goal_offset
        self.pacman.color = TEAL
        return True


class FruitAvailable(Task):
    #  Checks if there is a fruit available in the level
    def __init__(self, fruit):
        self.fruit = fruit

    def run(self) -> bool:
        if self.fruit is None:
            return False
        return True


class GetFruit(Task):
    #  Sets the fruit as Pacman's goal
    def __init__(self, fruit, pacman):
        self.fruit = fruit
        self.pacman = pacman

    def run(self) -> bool:
        self.pacman.goal = self.fruit.position
        return True


class EatPills(Task):
    #  Get's the closest pellet and sets it as goal for Pacman
    def __init__(self, pellet_group, pacman):
        self.pelletGroup = pellet_group
        self.pacman = pacman

    def run(self) -> bool:
        pellet = self.pelletGroup.getClosestPellet(self.pacman.position)
        self.pacman.goal = pellet.position
        self.pacman.color = YELLOW
        return True
