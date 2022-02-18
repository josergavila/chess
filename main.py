"""Main driver file. Handles user input and displays current GameState object"""
import os

import pygame as pg

import chess_engine
from settings import *


IMAGES = {}


def load_images():
    """Initializes a global dictionary of images"""
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(
            pg.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE)
        )


def draw_game_state(screen, game_state):
    """implements all graphics within current game state"""
    draw_board(screen)
    draw_pieces(screen, game_state.board)


def draw_board(screen):
    """Draws squares on board"""
    colors = [pg.Color("white"), pg.Color("gray")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            pg.draw.rect(
                screen, color, pg.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )


def draw_pieces(screen, board):
    """Draws pieces on board"""
    # NOTE: separate from draw_board to do syntax highlighting (less efficient)
    # NOTE: above square and below piece
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(
                    IMAGES[piece], pg.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                )


def main():
    """main driver --> Handles user input and update graphics"""
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))

    game_state = chess_engine.GameState()
    validMoves = game_state.get_valid_moves()
    move_made = False
    load_images()

    running = True
    square_selected = ()  # keeps track of last click
    player_clicks = []  # keeps track of players clicks
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif e.type == pg.MOUSEBUTTONDOWN:
                # (x, y) location of mouse
                location = pg.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if square_selected == (row, col):
                    # user clicked square twice
                    square_selected, player_clicks = (), []
                else:
                    square_selected = (row, col)
                    player_clicks.append(square_selected)

                if len(player_clicks) == 2:
                    move = chess_engine.Move(
                        player_clicks[0], player_clicks[1], game_state.board
                    )
                    if move in validMoves:
                        game_state.make_move(move)
                        move_made = True
                        square_selected = ()
                        player_clicks = []
                    else:
                        player_clicks = [square_selected]

            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_z:  # undo move
                    game_state.undo_move()
                    move_made = True

        if move_made:
            validMoves = game_state.get_valid_moves()
            move_made = False

        draw_game_state(screen, game_state)
        clock.tick(MAX_FPS)
        pg.display.flip()


if __name__ == "__main__":

    main()
