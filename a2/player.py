"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the player class hierarchy.
"""

import random
from typing import Optional
import pygame
from renderer import Renderer
from block import Block
from goal import Goal

TIME_DELAY = 600


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    renderer:
        The object that draws our Blocky board on the screen
        and tracks user interactions with the Blocky board.
    id:
        This player's number.  Used by the renderer to refer to the player,
        for example as "Player 2"
    goal:
        This player's assigned goal for the game.
    """
    renderer: Renderer
    id: int
    goal: Goal

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.renderer = renderer
        self.id = player_id

    def make_move(self, board: Block) -> int:
        """Choose a move to make on the given board, and apply it, mutating
        the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.
        """
        raise NotImplementedError


class HumanPlayer(Player):
    """A human player.

    A HumanPlayer can do a limited number of smashes.

    === Public Attributes ===
    num_smashes:
        number of smashes which this HumanPlayer has performed
    === Representation Invariants ===
    num_smashes >= 0
    """
    # === Private Attributes ===
    # _selected_block
    #     The Block that the user has most recently selected for action;
    #     changes upon movement of the cursor and use of arrow keys
    #     to select desired level.
    # _level:
    #     The level of the Block that the user selected
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0

    # The total number of 'smash' moves a HumanPlayer can make during a game.
    MAX_SMASHES = 1

    num_smashes: int
    _selected_block: Optional[Block]
    _level: int

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        super().__init__(renderer, player_id, goal)
        self.num_smashes = 0

        # This HumanPlayer has done no smashes yet.
        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._selected_block = None

    def process_event(self, board: Block,
                      event: pygame.event.Event) -> Optional[int]:
        """Process the given pygame <event>.

        Identify the selected block and mark it as highlighted.  Then identify
        what it is that <event> indicates needs to happen to <board>
        and do it.

        Return
           - None if <event> was not a board-changing move (that is, if was
             a change in cursor position, or a change in _level made via
            the arrow keys),
           - 1 if <event> was a successful move, and
           - 0 if <event> was an unsuccessful move (for example in the case of
             trying to smash in an invalid location or when the player is not
             allowed further smashes).
        """
        # Get the new "selected" block from the position of the cursor
        block = board.get_selected_block(pygame.mouse.get_pos(), self._level)

        # Remove the highlighting from the old "_selected_block"
        # before highlighting the new one
        if self._selected_block is not None:
            self._selected_block.highlighted = False
        self._selected_block = block
        self._selected_block.highlighted = True

        # Since get_selected_block may have not returned the block at
        # the requested level (due to the level being too low in the tree),
        # set the _level attribute to reflect the level of the block which
        # was actually returned.
        self._level = block.level

        if event.type == pygame.MOUSEBUTTONDOWN:
            block.rotate(event.button)
            return 1
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if block.parent is not None:
                    self._level -= 1
                return None

            elif event.key == pygame.K_DOWN:
                if len(block.children) != 0:
                    self._level += 1
                return None

            elif event.key == pygame.K_h:
                block.swap(0)
                return 1

            elif event.key == pygame.K_v:
                block.swap(1)
                return 1

            elif event.key == pygame.K_s:
                if self.num_smashes >= self.MAX_SMASHES:
                    print('Can\'t smash again!')
                    return 0
                if block.smash():
                    self.num_smashes += 1
                    return 1
                else:
                    print('Tried to smash at an invalid depth!')
                    return 0

    def make_move(self, board: Block) -> int:
        """Choose a move to make on the given board, and apply it, mutating
        the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.

        This method will hold focus until a valid move is performed.
        """
        self._level = 0
        self._selected_block = board

        # Remove all previous events from the queue in case the other players
        # have added events to the queue accidentally.
        pygame.event.clear()

        # Keep checking the moves performed by the player until a valid move
        # has been completed. Draw the board on every loop to draw the
        # selected block properly on screen.
        while True:
            self.renderer.draw(board, self.id)
            # loop through all of the events within the event queue
            # (all pending events from the user input)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 1

                result = self.process_event(board, event)
                self.renderer.draw(board, self.id)
                if result is not None and result > 0:
                    # un-highlight the selected block
                    self._selected_block.highlighted = False
                    return 0


class RandomPlayer(Player):
    """A random player.
    A RandomPlayer chooses moves randomly.
    A RandomPlayer can do unlimited times of smashes,
    but if it choose to smash a top level block or a unit cell, it forfeit
    that turn.
    """
    def make_move(self, board: Block) -> int:
        """Choose a random move to make on the given board, and apply it,
        mutating the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.
        Since this is a random player who always makes a random and complete
        move, this method always return 0.
        """
        x = random.randint(0, board.size)
        y = random.randint(0, board.size)
        rand_level = random.randint(0, board.max_depth)
        random_block = board.get_selected_block((x, y), rand_level)
        random_block.highlighted = True
        self.renderer.draw(board, self.id)
        pygame.time.wait(TIME_DELAY)
        random_act = random.randint(1, 5)
        if random_block.level == (0 or random_block.max_depth) and \
                random_act == 5:
            random_act = 6
        if random_act == 1:
            random_block.swap(0)
        elif random_act == 2:
            random_block.swap(1)
        elif random_act == 3:
            random_block.rotate(1)
        elif random_act == 4:
            random_block.rotate(3)
        elif random_act == 5:
            random_block.smash()
        else:
            pass
        random_block.highlighted = False
        self.renderer.draw(board, self.id)
        return 0


class SmartPlayer(Player):
    """A smart player.

    A SmartPlayer chooses a number of random moves and compare them
    to get the best move (relatively speaking).

    === Private Attributes ===
    _difficulty:
        The intelligence level of this Player:
        0: Compare 5 random moves
        1: Compare 10 random moves
        2: Compare 25 random moves
        3: Compare 50 random moves
        4: Compare 100 random moves
        5: Compare 150 random moves
        >5: Compare 150 random moves
    === Representation Invariants ===
    _difficulty >= 0
    """
    _difficulty: int

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal,
                 difficulty: int) -> None:
        """Initialize this SmartPlayer with the given <renderer>, <player_id>,
         <goal>, and <difficulty>.
        """
        super().__init__(renderer, player_id, goal)
        self._difficulty = difficulty

    def make_move(self, board: Block) -> int:
        """Generate a number of moves to compare based on self._difficulty, then
        find the best move from the list of moves generated
        """
        random_act = random.randint(1, 4)
        moves = []
        # each move will be a tuple containing the point
        # difference of before and after the move, the code of the move, and
        # the Block on which the move will be performed.

        num_moves_to_compare = self._get_moves()

        # loop until we get a list of random moves
        while len(moves) < num_moves_to_compare:
            x = random.randint(0, board.size)
            y = random.randint(0, board.size)
            rand_level = random.randint(0, board.max_depth)
            random_block = board.get_selected_block((x, y), rand_level)
            if random_act == 1:
                pt_before = self.goal.score(board)
                random_block.swap(0)
                point_diff = self.goal.score(board) - pt_before
                moves.append((point_diff, random_act, random_block))
                random_block.swap(0)
            elif random_act == 2:
                pt_before = self.goal.score(board)
                random_block.swap(1)
                point_diff = self.goal.score(board) - pt_before
                moves.append((point_diff, random_act, random_block))
                random_block.swap(1)
            elif random_act == 3:
                pt_before = self.goal.score(board)
                random_block.rotate(1)
                point_diff = self.goal.score(board) - pt_before
                moves.append((point_diff, random_act, random_block))
                random_block.rotate(3)
            elif random_act == 4:
                pt_before = self.goal.score(board)
                random_block.rotate(3)
                point_diff = self.goal.score(board) - pt_before
                moves.append((point_diff, random_act, random_block))
                random_block.rotate(1)
        # Now we find the best move from the randomly generated list
        best_move = moves[0]
        for move in moves:
            if move[0] > best_move[0]:
                best_move = move
        # Perform that move!
        best_move[2].highlighted = True
        self.renderer.draw(board, self.id)
        if best_move[1] == 1:
            best_move[2].swap(0)
        elif best_move[1] == 2:
            best_move[2].swap(1)
        elif best_move[1] == 3:
            best_move[2].rotate(1)
        elif best_move[1] == 4:
            best_move[2].rotate(3)
        pygame.time.wait(TIME_DELAY)
        best_move[2].highlighted = False
        self.renderer.draw(board, self.id)
        return 0

    def _get_moves(self) -> int:
        """Helper method for make move, returns the number of moves
        to generate based on this SmartPlayer's difficulty level."""
        num_moves_to_compare = 5
        if self._difficulty == 1:
            num_moves_to_compare = 10
        elif self._difficulty == 2:
            num_moves_to_compare = 25
        elif self._difficulty == 3:
            num_moves_to_compare = 50
        elif self._difficulty == 4:
            num_moves_to_compare = 100
        elif self._difficulty >= 5:
            num_moves_to_compare = 150
        return num_moves_to_compare


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer',
            'pygame'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
