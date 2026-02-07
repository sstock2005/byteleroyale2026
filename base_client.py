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

def determine_movement(current_position: Vector, goal_position: Vector, world: GameBoard, my_avatar: Avatar) -> ActionType | None:
    """Helper method to determine the next movement action based on current position and goal position."""
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
        """
        This is where your AI will decide what to do.
        :param turn:        The current turn of the game.
        :param actions:     This is the actions object that you will add effort allocations or decrees to.
        :param world:       Generic world information
        """
        
        current_position = avatar.position
        coins = world.get_objects(ObjectType.COIN_SPAWNER).keys()
        closest_coin = get_closest_goal(current_position, coins)
        movement_action = determine_movement(current_position, closest_coin, world, avatar)
        
        if movement_action is not None:
            return [movement_action]
        return []
