"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Goal class hierarchy.
"""

from typing import List, Tuple
from block import Block


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """A goal to create the maximum amount of perimeter of this goal's target
        colour, on the for sides of the given board.
    """

    def score(self, board: Block) -> int:
        """A method of class PerimeterGoal that calculates the score and return
        the score.
        Score is calculated by counting the number of unit cells with target
        colour on the four sides (perimeter) of the given board.
        """
        flattened_lst = board.flatten()
        score = 0
        for i in flattened_lst[0]:
            if i == self.colour:
                score += 1
        for i in flattened_lst[len(flattened_lst) - 1]:
            if i == self.colour:
                score += 1
        for i in flattened_lst:
            if i[0] == self.colour:
                score += 1
            if i[len(flattened_lst) - 1] == self.colour:
                score += 1

        return score

    def description(self) -> str:
        """Return the type and description of goal to indicate the type of goal
        of the game and describe this type of Goal.
        Here, the type of goal is Perimeter Goal.
        """
        return "Perimeter Goal: Put blocks of target colour to the perimeter!"


class BlobGoal(Goal):
    """A goal to create the largest connected blob of this goal's target
    colour, anywhere within the Block.
    """

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
           -1  if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        size = 0
        colour = board[pos[0]][pos[1]]
        if colour != self.colour:
            visited[pos[0]][pos[1]] = 0
            return 0
        elif colour == self.colour and visited[pos[0]][pos[1]] == -1:
            size += 1
            visited[pos[0]][pos[1]] = 1

            if pos[1] < len(visited) - 1:
                size += self._undiscovered_blob_size((pos[0], pos[1] + 1),
                                                     board, visited)
            if pos[1] != 0:
                size += self._undiscovered_blob_size((pos[0], pos[1] - 1),
                                                     board, visited)
            if pos[0] < len(visited) - 1:
                size += self._undiscovered_blob_size((pos[0] + 1, pos[1]),
                                                     board, visited)
            if pos[0] != 0:
                size += self._undiscovered_blob_size((pos[0] - 1, pos[1]),
                                                     board, visited)
            return size
        else:
            return 0

    def score(self, board: Block) -> int:
        """A method of class BlobGoal that calculates the score and return
        the score.
        Score is calculated by counting the size of the largest connected
        blob of this goal's target colour, anywhere within the given board.
        """
        flattened_board = board.flatten()
        visited = []
        length = len(flattened_board)
        for _ in range(length):
            lst = []
            for i in range(length):
                lst.append(-1)
            visited.append(lst)
        lst = []
        for i in range(length):
            for j in range(length):
                lst.append(self._undiscovered_blob_size((i, j),
                                                        flattened_board,
                                                        visited))
        return max(lst)

    def description(self) -> str:
        """Return the type and description of goal to indicate the type of goal
        of the game and describe this type of Goal.
        Here, the type of goal is Blob Goal.
        """
        return "Blob Goal: Join target colour blocks together into one blob!"


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer'
        ],
        'max-attributes': 15
    })
