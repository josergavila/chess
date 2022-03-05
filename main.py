"""Main driver file. Handles user input and displays current GameState object"""
import os

import pygame as pg

import chess_engine
import chess_ai as ai
from settings import *

# ======================
# GLOBAL VARIABLES
IMAGES = {}
COLORS = [pg.Color("white"), pg.Color("gray")]
# ======================


def main():
    """main driver --> Handles user input and update graphics"""
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))

    game_state = chess_engine.GameState()
    valid_moves = game_state.get_valid_moves()
    move_made, animate = False, False
    load_images()

    running = True
    square_selected = ()  # keeps track of last click
    player_clicks = []  # keeps track of players clicks
    game_over = False
    player_one, player_two = True, False
    while running:
        human_turn = is_human_turn(game_state, player_one, player_two)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN and not game_over and human_turn:
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
                    for valid_move in valid_moves:
                        if move == valid_move:
                            # for move in valid_moves:
                            game_state.make_move(valid_move)
                            move_made, animate = True, True
                            square_selected = ()
                            player_clicks = []

                        if not move_made:
                            player_clicks = [square_selected]

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_z:  # press z -> undo move
                    game_state.undo_move()
                    move_made, animate = True, False

                if event.key == pg.K_r:  # press r -> reset board
                    game_state = chess_engine.GameState()
                    valid_moves = game_state.get_valid_moves()
                    square_selected, player_clicks = (), []
                    move_made, animate, game_over = False, False, False

        if not game_over and not human_turn:
            ai_move = ai.find_best_move(game_state, valid_moves)
            if not ai_move:
                ai_move = ai.find_random_move(valid_moves)
            game_state.make_move(ai_move)
            move_made, animate = True, True

        if move_made:
            if animate:
                animate_move(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.get_valid_moves()
            move_made = False

        draw_game_state(screen, game_state, valid_moves, square_selected)

        if game_state.check_mate:
            game_over = True
            winner_color = "Black" if game_state.white_to_move else "White"
            draw_text(screen, f"{winner_color} wins by checkmate!")
        elif game_state.stale_mate:
            game_over = True
            draw_text(screen, "Stalemate!")

        clock.tick(MAX_FPS)
        pg.display.flip()


def load_images():
    """Initializes a global dictionary of images"""
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(
            pg.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE)
        )


def is_human_turn(game_state, player_one, player_two):
    return (game_state.white_to_move and player_one) or (
        not game_state.white_to_move and player_two
    )


def draw_game_state(screen, game_state, valid_moves, square_selected):
    """implements all graphics within current game state"""
    draw_board(screen)
    highlight_squares(screen, game_state, valid_moves, square_selected)
    draw_pieces(screen, game_state.board)


def highlight_squares(screen, game_state, valid_moves, square_selected):
    """Highlights square selected and moves for piece selected"""
    if not square_selected:
        return

    row, col = square_selected
    if is_piece_color_same_as_player_color(game_state, row, col):
        surface = pg.Surface((SQ_SIZE, SQ_SIZE))
        surface.set_alpha(100)  # add a little transparency
        surface.fill(pg.Color("blue"))
        screen.blit(surface, (col * SQ_SIZE, row * SQ_SIZE))
        surface.fill(pg.Color("yellow"))
        for move in valid_moves:
            if move.start_row == row and move.start_col == col:
                screen.blit(surface, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))


def is_piece_color_same_as_player_color(game_state, row, col):
    player_color = "w" if game_state.white_to_move else "b"
    return game_state.board[row][col][0] == player_color


def draw_board(screen):
    """Draws squares on board"""
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = COLORS[((row + col) % 2)]
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


def animate_move(move, screen, board, clock):
    delta_row = move.end_row - move.start_row
    delta_col = move.end_col - move.start_col
    frames_per_square = 10  # frames to move one square
    frame_count = (abs(delta_row) + abs(delta_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row = move.start_row + delta_row * (frame / frame_count)
        col = move.start_col + delta_col * (frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = COLORS[(move.end_row + move.end_col) % 2]
        end_square = pg.Rect(
            move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE
        )
        pg.draw.rect(screen, color, end_square)
        if move.piece_captured != "--":
            screen.blit(IMAGES[move.piece_captured], end_square)
        screen.blit(
            IMAGES[move.piece_moved],
            pg.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE),
        )
        pg.display.flip()
        clock.tick(60)


def draw_text(screen, message):
    font = pg.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(message, 0, pg.Color("Gray"))
    text_location = pg.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH // 2 - text_object.get_width() / 2,
        HEIGHT / 2 - text_object.get_height() / 2,
    )
    screen.blit(text_object, text_location)
    text_object = font.render(message, 0, pg.Color("Black"))
    screen.blit(text_object, text_location.move(2, 2))


if __name__ == "__main__":

    main()
