from game.client.user_client import UserClient
from game.common.avatar import Avatar
from game.common.enums import ObjectType, ActionType
from game.common.map.game_board import GameBoard
from game.constants import *
from game.common.enums import ActionType, ObjectType
from game.common.map.occupiable import Occupiable
from game.constants import DIRECTION_TO_MOVE
from game.utils.vector import Vector

import heapq
from typing import Dict, List, Tuple, Optional
from game.common.game_object import GameObject

from math import dist

GEN_1_DONE = False
SCRAP_1_DONE = False
COIN_1_DONE = False
COIN_2_DONE = False
BATTERY_1_DONE = False

def get_closest_goal(u: Vector, l):
    """Helper method to determine the closest goal given a vector and a list of goal vectors"""
    maximum = float(1000)
    goal = None
    for v in l:
        d = dist(u.as_tuple(), v.as_tuple())
        if d <= maximum:
            maximum = d
            goal = v
    return goal

def invert_movement(movement_action: ActionType) -> ActionType | None:
    match movement_action:
        case ActionType.MOVE_DOWN:
            return ActionType.MOVE_UP
        case ActionType.MOVE_UP:
            return ActionType.MOVE_DOWN
        case ActionType.MOVE_LEFT:
            return ActionType.MOVE_RIGHT
        case ActionType.MOVE_RIGHT:
            return ActionType.MOVE_LEFT
        case _:
            return None

Position = Tuple[int, int]

DIRECTIONS = [(1,0), (-1,0), (0,1), (0,-1)]

def a_star_move(start: Vector, goal: Vector, world, allow_vents: bool = True, game_object: GameObject | None = None) -> ActionType | None:
    path = a_star_path(
        start=start,
        goal=goal,
        world=world,
        allow_vents=allow_vents,
        game_object=game_object
    )

    if not path or len(path) < 2:
        return None

    next_step: Vector = path[1]
    direction = next_step - start
    action = DIRECTION_TO_MOVE.get(direction)
    return action

def a_star_path(start: Vector, goal: Vector, world, allow_vents = True, game_object: GameObject | None = None) -> Optional[List[Vector]]:
    start_p = (start.x, start.y)
    goal_p = (goal.x, goal.y)

    frontier = [(0, start_p)]
    came_from = {start_p: None}
    cost = {start_p: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal_p:
            path = []
            while current is not None:
                x, y = current
                path.insert(0, Vector(x, y))
                current = came_from[current]
            return path

        for dx, dy in DIRECTIONS:
            nxt = (current[0] + dx, current[1] + dy)
            vec = Vector(nxt[0], nxt[1])

            if game_object is not None and not world.can_object_occupy(vec, game_object):
                continue

            if not world.is_valid_coords(vec):
                continue

            top = world.get_top(vec)
            if top and top.object_type != ObjectType.AVATAR:
                # walls block
                if top.object_type == ObjectType.WALL:
                    continue

                # vents block unless allowed
                if top.object_type == ObjectType.VENT and not allow_vents:
                    continue

                if top.object_type == ObjectType.DUMB_BOT:
                    continue

                # can't pass through non-occupiable
                if not isinstance(top, Occupiable):
                    continue

            new_cost = cost[current] + 1
            if nxt not in cost or new_cost < cost[nxt]:
                cost[nxt] = new_cost
                priority = new_cost + vec.distance(goal)
                heapq.heappush(frontier, (priority, nxt))
                came_from[nxt] = current

    return None

def object_in_inventory(object: ObjectType, avatar: Avatar) -> bool:
    for i in avatar.inventory:
        if i is not None:
            if i.object_type == object:
                return True
    return False

class Client(UserClient):

    def __init__(self):
        super().__init__()

    def team_name(self) -> str:
        """
        Allows the team to set a team name.
        :return: Your team name
        """
        return "eroorororor"

    def take_turn(self, turn: int, world: GameBoard, avatar: Avatar) -> list[ActionType]:
        global SCRAP_1_DONE, GEN_1_DONE, COIN_1_DONE, COIN_2_DONE, SCRAP_2_DONE, BATTERY_1_DONE, COIN_1_DONE_AGAIN

        """
        This is where your AI will decide what to do.
        :param turn:        The current turn of the game.
        :param actions:     This is the actions object that you will add effort allocations or decrees to.
        :param world:       Generic world information
        """
        
        # positions
        current_position = avatar.position
        scrap_1_position = Vector(7, 8)
        gen_1_position = Vector(1, 8)
        coin_1_position = Vector(4, 6)
        coin_2_position = Vector(12, 2)
        scrap_2_position = Vector(17, 4)
        battery_1_position = Vector(16, 1)
        dumb_bot_position = list(world.get_objects(ObjectType.DUMB_BOT).keys())[0]

        if avatar.power < current_position.distance(battery_1_position):
            movement_action = a_star_move(
                current_position,
                battery_1_position,
                world,
                False,
                avatar
            )
            if movement_action is not None:
                return [movement_action]

        # grab first scrap
        if SCRAP_1_DONE == False:
            movement_action = a_star_move(
                current_position,
                scrap_1_position,
                world,
                False,
                avatar
            )
            if movement_action is not None:
                return [movement_action]
            else:
                SCRAP_1_DONE = True

        # activate first generator and grab another scrap
        if GEN_1_DONE == False:
            movement_action = a_star_move(
                current_position,
                gen_1_position,
                world,
                False,
                avatar
            )
            if movement_action is not None:
                return [movement_action]
            else:
                GEN_1_DONE = True
                SCRAP_1_DONE = False # grab scrap again
                return [ActionType.INTERACT_LEFT]

        # grab 1st coin and grab another scrap
        if COIN_1_DONE == False:
            movement_action = a_star_move(
                current_position,
                coin_1_position,
                world,
                False,
                avatar
            )
            if movement_action is not None:
                return [movement_action]
            else:
                COIN_1_DONE = True
                SCRAP_1_DONE = False # grab scrap again

        # grab 2nd coin
        if COIN_2_DONE == False:
            movement_action = a_star_move(
                current_position,
                coin_2_position,
                world,
                False,
                avatar
            )
            if movement_action is not None:
                return [movement_action]
            else:
                COIN_2_DONE = True

        # grab 1st battery
        if BATTERY_1_DONE == False:
            movement_action = a_star_move(
                current_position,
                battery_1_position,
                world,
                False,
                avatar
            )
            if movement_action is not None:
                return [movement_action]

        return []