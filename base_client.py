from game.client.user_client import UserClient
from game.common.avatar import Avatar
from game.common.enums import ObjectType, ActionType
from game.common.map.game_board import GameBoard
from game.constants import *
from game.common.enums import ActionType, ObjectType
from game.common.map.occupiable import Occupiable
from game.constants import DIRECTION_TO_MOVE
from game.utils.vector import Vector

from math import dist

SCRAP_1_DONE = False
GEN_1_DONE = False
COIN_1_DONE = False
COIN_2_DONE = False
SCRAP_2_DONE = False
BATTERY_1_DONE = False
COIN_1_DONE_AGAIN = False
COIN_2_DONE_AGAIN = False
BATTERY_1_DONE_AGAIN = False
GEN_2_DONE = False
COIN_3_DONE = False
BATTERY_2_DONE = False
COIN_4_DONE = False
SCRAP_3_DONE = False
GEN_3_DONE = False

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

def backup_panic_movemvent(current_position: Vector, bot: Vector, world: GameBoard, my_avatar: Avatar) -> ActionType | None:
    if current_position.y < bot.y:
        # move up
        new_position = Vector(current_position.x - 2, current_position.y - 2)
        if world.can_object_occupy(new_position, my_avatar):
            return ActionType.MOVE_UP
    elif current_position.y > bot.y:
        # move down
        new_position = Vector(current_position.x + 2, current_position.y + 2)
        if world.can_object_occupy(new_position, my_avatar):
            return ActionType.MOVE_DOWN
    elif current_position.x < bot.x:
        # move left
        new_position = Vector(current_position.x - 2, current_position.y - 2)
        if world.can_object_occupy(new_position, my_avatar):
            return ActionType.MOVE_LEFT
    elif current_position.x > bot.x:
        # move right
        new_position = Vector(current_position.x + 2, current_position.y + 2)
        if world.can_object_occupy(new_position, my_avatar):
            return ActionType.MOVE_RIGHT
        
    # print("no panic action!")
    return None

import heapq
from typing import Dict, List, Tuple, Optional
from game.common.enums import ActionType, ObjectType
from game.common.game_object import GameObject
from game.common.map.occupiable import Occupiable
from game.constants import DIRECTION_TO_MOVE
from game.utils.vector import Vector

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

def determine_movement(current_position: Vector, goal_position: Vector, world: GameBoard, my_avatar: Avatar, dumb_bot: Vector, doe_bot: Vector, crawler_bot: Vector) -> ActionType | None:
    """Helper method to determine the next movement action based on current position and goal position."""
    
    # print(f"Distance from Dumb Bot: {current_position.distance(dumb_bot)}")
    # print(f"Distance from Doe Bot: {current_position.distance(doe_bot)}")
    # print(f"Distance from Crawler Bot: {current_position.distance(crawler_bot)}")
    
    if my_avatar.health < 2:
        if current_position.distance(dumb_bot) < 3:
            panic_movement = backup_panic_movemvent(current_position, dumb_bot, world, my_avatar)
            if panic_movement is not None:
                return panic_movement
            else:
                return None

        if current_position.distance(doe_bot) < 3:
            panic_movement = backup_panic_movemvent(current_position, doe_bot, world, my_avatar)
            if panic_movement is not None:
                return panic_movement
            else:
                return None

        if current_position.distance(crawler_bot) < 3:
            panic_movement = backup_panic_movemvent(current_position, crawler_bot, world, my_avatar)
            if panic_movement is not None:
                return panic_movement
            else:
                return None

    return a_star_move(current_position, goal_position, world, True, my_avatar)

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
        global SCRAP_1_DONE, GEN_1_DONE, COIN_1_DONE, COIN_2_DONE, SCRAP_2_DONE, BATTERY_1_DONE, \
        COIN_1_DONE_AGAIN, COIN_2_DONE_AGAIN, BATTERY_1_DONE_AGAIN, GEN_2_DONE, COIN_3_DONE, \
        BATTERY_2_DONE, COIN_4_DONE, GEN_3_DONE, SCRAP_3_DONE

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
        gen_2_position = Vector(29, 18)
        coin_3_position = Vector(34, 17)
        battery_2_position = Vector(36, 6)
        coin_4_position = Vector(32, 7)
        scrap_3_position = Vector(32, 4)
        gen_3_position = Vector(35, 2)
        dumb_bot_position = list(world.get_objects(ObjectType.DUMB_BOT).keys())[0]
        doe_bot_position = list(world.get_objects(ObjectType.JUMPER_BOT).keys())[0]
        crawler_bot_position = list(world.get_objects(ObjectType.CRAWLER_BOT).keys())[0]

        # grab first scrap
        if SCRAP_1_DONE == False:
            movement_action = determine_movement(
                current_position,
                scrap_1_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                SCRAP_1_DONE = True
                GEN_1_DONE = False

        # activate first generator and grab another scrap
        if GEN_1_DONE == False:
            movement_action = determine_movement(
                current_position,
                gen_1_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                GEN_1_DONE = True
                print("got gen")
                SCRAP_1_DONE = False # grab scrap again
                return [ActionType.INTERACT_LEFT]

        # grab 1st coin and grab another scrap
        if COIN_1_DONE == False:
            movement_action = determine_movement(
                current_position,
                coin_1_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                COIN_1_DONE = True
                SCRAP_1_DONE = False # grab scrap again

        # grab 2nd coin
        if COIN_2_DONE == False:
            movement_action = determine_movement(
                current_position,
                coin_2_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                COIN_2_DONE = True

        # grab 2nd scrap
        if SCRAP_2_DONE == False:
            movement_action = determine_movement(
                current_position,
                scrap_2_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                SCRAP_2_DONE = True

        # grab 1st battery
        if BATTERY_1_DONE == False:
            movement_action = determine_movement(
                current_position,
                battery_1_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                BATTERY_1_DONE = True

        # grab 1st coin again
        if COIN_1_DONE_AGAIN == False:
            movement_action = determine_movement(
                current_position,
                coin_1_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                COIN_1_DONE_AGAIN = True
                
        # grab 2nd coin again
        if COIN_2_DONE_AGAIN == False:
            movement_action = determine_movement(
                current_position,
                coin_2_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                COIN_2_DONE_AGAIN = True

        # grab 1st battery and grab scrap 2 again
        if BATTERY_1_DONE_AGAIN == False:
            movement_action = determine_movement(
                current_position,
                battery_1_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                BATTERY_1_DONE_AGAIN = True
                SCRAP_2_DONE = False
                
        # get coin 4
        if COIN_4_DONE == False:
            movement_action = determine_movement(
                current_position,
                coin_4_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                COIN_4_DONE = True

        # activate 2nd gen
        if GEN_2_DONE == False:
            movement_action = determine_movement(
                current_position,
                gen_2_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                GEN_2_DONE = True
                return [ActionType.INTERACT_RIGHT]

        # collection coin 3
        if COIN_3_DONE == False:
            movement_action = determine_movement(
                current_position,
                coin_3_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                COIN_3_DONE = True

        # get battery 2
        if BATTERY_2_DONE == False:
            movement_action = determine_movement(
                current_position,
                battery_2_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                BATTERY_2_DONE = True

        # get scrap 3
        if SCRAP_3_DONE == False:
            movement_action = determine_movement(
                current_position,
                scrap_3_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                COIN_3_DONE = True

        # activate gen 3
        if GEN_3_DONE == False:
            movement_action = determine_movement(
                current_position,
                gen_3_position,
                world,
                avatar,
                dumb_bot_position,
                doe_bot_position,
                crawler_bot_position)
            if movement_action is not None:
                return [movement_action]
            else:
                GEN_3_DONE = True
                return [ActionType.INTERACT_UP]
        return []