import random

# ======================
# GLOBAL VARIABLES
PIECE_SCORES = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1, "--": None}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3
# ======================


def find_random_move(valid_moves):
    """picks a random valid move"""
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def find_best_material_move(game_state, valid_moves):
    """picks best move based on material -> looking two moves ahead (greedy algo)"""
    turn_multiplier = 1 if game_state.white_to_move else -1
    opponent_min_max_score, best_player_move = CHECKMATE, None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        game_state.make_move(player_move)
        opponents_moves = game_state.get_valid_moves()
        opponent_max_score = -CHECKMATE
        if game_state.stale_mate:
            opponent_min_max_score = STALEMATE
            continue

        opponent_min_max_score = -CHECKMATE
        if game_state.check_mate:
            continue

        for opponent_move in opponents_moves:
            game_state.make_move(opponent_move)
            game_state.get_valid_moves()
            if game_state.check_mate:
                score = CHECKMATE
            elif game_state.stale_mate:
                score = STALEMATE
            else:
                score = -turn_multiplier * score_material(game_state.board)
            if score > opponent_max_score:
                opponent_max_score = score
            game_state.undo_move()
        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move
        game_state.undo_move()

    return best_player_move


def score_material(board):
    """scores board based on material - greedy algo"""
    score = 0
    for row in board:
        for square in row:
            if "--" == square:
                continue

            color, piece_score = square[0], PIECE_SCORES[square[1]]
            if color == "w":
                score += piece_score
            elif color == "b":
                score -= piece_score

    return score


def find_best_move(game_state, valid_moves):
    """helper to make first recursive call"""
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    # find_move_min_max(game_state, valid_moves, DEPTH, game_state.white_to_move)
    turn_multiplier = 1 if game_state.white_to_move else -1
    find_move_nega_max_alpha_beta(
        game_state, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, turn_multiplier
    )

    return next_move


def find_move_min_max(game_state, valid_moves, depth, white_to_move):
    """minmax algo"""
    global next_move
    if not depth:
        return score_material(game_state.board)

    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            game_state.make_move(move)
            next_moves = game_state.get_valid_moves()
            score = find_move_min_max(game_state, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            game_state.undo_move()
        return max_score
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            game_state.make_move(move)
            next_moves = game_state.get_valid_moves()
            score = find_move_min_max(game_state, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            game_state.undo_move()
        return min_score


def find_move_nega_max(game_state, valid_moves, depth, turn_multiplier):
    """nega max algo"""
    global next_move
    if not depth:
        return turn_multiplier * score_board(game_state)

    max_score = -CHECKMATE
    for move in valid_moves:
        game_state.make_move(move)
        next_moves = game_state.get_valid_moves()
        score = -find_move_nega_max(game_state, next_moves, depth - 1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move

        game_state.undo_move()

    return max_score


def find_move_nega_max_alpha_beta(
    game_state, valid_moves, depth, alpha, beta, turn_multiplier
):
    """nega max algo"""
    global next_move
    if not depth:
        return turn_multiplier * score_board(game_state)

    max_score = -CHECKMATE
    for move in valid_moves:
        game_state.make_move(move)
        next_moves = game_state.get_valid_moves()
        score = -find_move_nega_max_alpha_beta(
            game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier
        )

        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        game_state.undo_move()

        if max_score > alpha:
            alpha = max_score

        if alpha >= beta:
            break

    return max_score


def score_board(game_state):
    """positive score -> good for white; negative score -> good for black"""
    if game_state.check_mate:
        return -CHECKMATE if game_state.white_to_move else CHECKMATE
    elif game_state.stale_mate:
        return STALEMATE

    score = 0
    for row in game_state.board:
        for square in row:
            if "--" == square:
                continue

            color, piece_score = square[0], PIECE_SCORES[square[1]]
            if color == "w":
                score += piece_score
            elif color == "b":
                score -= piece_score

    return score
