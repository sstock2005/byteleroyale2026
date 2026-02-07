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

    if current_position.y > goal_position.y:
        # need to move up
        new_position = Vector(current_position.x, current_position.y - 1)
        if world.can_object_occupy(new_position, my_avatar):
            return ActionType.MOVE_UP
    if current_position.y < goal_position.y:
        # need to move down
        new_position = Vector(current_position.x, current_position.y + 1)
        if world.can_object_occupy(new_position, my_avatar):
            return ActionType.MOVE_DOWN
    if current_position.x < goal_position.x:
        # need to move right
        new_position = Vector(current_position.x + 1, current_position.y)
        if world.can_object_occupy(new_position, my_avatar):
            return ActionType.MOVE_RIGHT
    if current_position.x > goal_position.x:
        # need to move left
        new_position = Vector(current_position.x - 1, current_position.y)
        if world.can_object_occupy(new_position, my_avatar):
            return ActionType.MOVE_LEFT
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
        gen_2_position = Vector(28, 18)
        coin_3_position = Vector(34, 17)
        battery_2_position = Vector(36, 6)
        coin_4_position = Vector(31, 7)
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