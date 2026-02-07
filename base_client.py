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

# def get_closest_goal(u: Vector, l):
#     maximum = float(1000)
#     for v in l:
#         d = dist(u.as_tuple(), v.as_tuple())
#          if d <= maximum:
#             maximum = d
            
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
        
        match turn:
            case 1:
                return [ActionType.MOVE_RIGHT]
            case 2:
                return [ActionType.MOVE_RIGHT]
            case 3:
                return [ActionType.MOVE_RIGHT]
            case 4:
                return [ActionType.MOVE_DOWN]
            case 5:
                return [ActionType.MOVE_DOWN]
            case 6:
                return [ActionType.MOVE_DOWN]
            case 7:
                return [ActionType.MOVE_DOWN]
            case 8:
                return [ActionType.MOVE_DOWN]
        return []