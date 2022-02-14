"""Main driver file. Handles user input and displays current GameState object"""
import os

import pygame as p

from chess_engine import GameState
from settings import *


IMAGES = {}


def load_images():
    """Initializes a global dictionary of images"""
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE)
        )


def draw_game_state(screen, gs):
    """implements all graphics within current game state"""
    draw_board(screen)
    draw_pieces(screen, gs.board)


def draw_board(screen):
    """Draws squares on board"""
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(
                screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
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
                    IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                )


def main():
    """main driver --> Handles user input and update graphics"""
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = GameState()
    load_images()
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


if __name__ == "__main__":

    main()
