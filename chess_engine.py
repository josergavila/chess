"""Stares all information about current state of chess game. Determines valid moves of current state and keeps move log."""


class GameState:

    rook_directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # vertical moves
    bishop_directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # diagonal moves
    knight_moves = (
        (-2, -1),
        (-2, 1),
        (-1, -2),
        (-1, 2),
        (1, -2),
        (1, 2),
        (2, -1),
        (2, 1),
    )
    king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
    directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

    def __init__(self):
        # more efficient implementation would be with numpy arrays
        # board is a 8x8 2d list
        # first character represents color of piece
        # second character represents type of piece
        # "--" represents an empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.move_functions = {
            "p": self._get_pawn_moves,
            "R": self._get_rook_moves,
            "N": self._get_knight_moves,
            "B": self._get_bishop_moves,
            "Q": self._get_queen_moves,
            "K": self._get_king_moves,
        }
        self.white_to_move = True
        self.move_log = []

        # valid moves attributes
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.check_mate = False
        self.stale_mate = False

    def make_move(self, move):
        """executes move (does not work for castling, pawn promotion and en-passant"""
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        if "K" in move.piece_moved:  # update king location
            self._update_king_location(move.piece_moved[0], move.end_row, move.end_col)

    def undo_move(self):
        """undo last move"""
        assert self.move_log

        move = self.move_log.pop()
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured
        self.white_to_move = not self.white_to_move
        if "K" in move.piece_moved:
            self._update_king_location(
                move.piece_moved[0], move.start_row, move.start_col
            )

    def get_valid_moves(self):
        """all moves considering checks/rules"""
        # naive implementation ->  inefficient method
        # 1) generate all possible moves and make move
        # 2) generate opponent's moves
        # 3) for each opponent's move, check if king is attacked
        # 4) if king is attacked it's not a valid move
        moves = self.get_all_possible_moves()
        for move in moves[::-1]:
            self.make_move(move)
            self.white_to_move = not self.white_to_move  # make_move changes turn
            if self._is_in_check():
                moves.remove(move)
            self.white_to_move = not self.white_to_move
            self.undo_move()
        self._is_check_mate(moves)

        return moves

    def check_for_pins_and_checks(self):
        pins, checks, in_check = [], [], False
        enemy_color = self._get_enemy_color()
        player_color = self._get_player_color()
        start_row, start_col = self._get_king_location()

        for direction in self.directions:
            row_dir, col_dir = direction
            possible_pin = ()
            for i in range(1, 8):
                end_row = start_row + row_dir * i
                end_col = start_col + col_dir * i
                if not self._is_on_board(end_row, end_col):  # off board
                    break

                end_piece = self.board[end_row][end_col]
                if end_piece[0] == player_color:
                    if possible_pin:  # pin - piece protecting king
                        possible_pin = (end_row, end_col, row_dir, col_dir)
                    else:
                        break  # two pieces in direction - no pin
                elif end_piece == enemy_color:
                    piece_type = end_piece[1]
                    if (
                        self._is_rook(direction, piece_type)
                        or self._is_bishop(direction, piece_type)
                        or (
                            self._is_pawn(i, piece_type)
                            and self._is_there_pawn_threat(enemy_color, direction)
                        )
                        or self._is_king(i, piece_type)
                    ):
                        if possible_pin == ():
                            in_check = True
                            checks.append((end_row, end_col, row_dir, col_dir))
                            break
                        else:  # piece blocking -> pin
                            pins.append(possible_pin)
                            break

        for row_dir, col_dir in self.knight_moves:  # check for knights
            end_row = start_row + row_dir
            end_col = start_col + col_dir
            if not self._is_on_board(end_row, end_col):  # off board
                break

            end_piece = self.board[end_row][end_col]
            if end_piece[0] == enemy_color and end_piece[1] == "N":
                in_check = True
                checks.append((end_row, end_col, row_dir, col_dir))

        return in_check, pins, checks

    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if self._is_white_turn(turn) or self._is_black_turn(turn):
                    piece = self.board[row][col][1]
                    self.move_functions[piece](row, col, moves)

        return moves

    # ==============================================================
    # private helper methods
    # ==============================================================

    def _update_king_location(self, piece_color, row, col):
        if piece_color == "w":
            self.white_king_location = (row, col)
        else:
            self.black_king_location = (row, col)

    def _get_king_location(self):
        if self.white_to_move:
            return self.white_king_location
        else:
            return self.black_king_location

    def _is_rook(self, direction, piece_type):
        return direction in self.rook_directions and piece_type == "R"

    def _is_bishop(self, direction, piece_type):
        return direction in self.bishop_directions and piece_type == "B"

    def _is_queen(self, piece_type):
        return piece_type == "Q"

    def _is_pawn(self, direction_range, piece_type):
        return direction_range == 1 and piece_type == "p"

    def _is_king(self, direction_range, piece_type):
        return direction_range == 1 and piece_type == "K"

    def _is_in_check(self):
        if self.white_to_move:
            return self._is_square_under_attack(self.white_king_location)
        else:
            return self._is_square_under_attack(self.black_king_location)

    def _is_square_under_attack(self, square):
        row, col = square
        self.white_to_move = not self.white_to_move
        opponent_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opponent_moves:
            if move.end_row == row and move.end_col == col:  # square is under attack
                return True
        return False

    def _is_check_mate(self, moves):
        self.check_mate, self.stale_mate = False, False
        if not moves:
            if self._is_in_check():
                self.check_mate = True
            else:
                self.stale_mate = True

    def _is_white_turn(self, turn):
        return turn == "w" and self.white_to_move

    def _is_black_turn(self, turn):
        return turn == "b" and not self.white_to_move

    def _get_enemy_color(self):
        return "b" if self.white_to_move else "w"

    def _get_player_color(self):
        return "w" if self.white_to_move else "b"

    def _get_color_direction(self):
        return -1 if self.white_to_move else 1

    def _append_move(self, start_square, end_square, moves):
        moves.append(self._instantiate_move(start_square, end_square))

    def _instantiate_move(self, start_square, end_square):
        return Move(start_square, end_square, self.board)

    # ==============================================================
    # static methods
    # ==============================================================

    @staticmethod
    def _is_on_board(row, col):
        return (0 <= row < 8) and (0 <= col < 8)

    @staticmethod
    def _is_there_pawn_threat(piece_color, piece_direction):
        if piece_color == "w" and piece_direction in ((1, -1), (1, 1)):
            return True
        elif piece_color == "b" and piece_direction in ((-1, -1), (-1, 1)):
            return True
        else:
            return False

    # ==============================================================
    # piece move methods
    # ==============================================================

    def _get_pawn_moves(self, row, col, moves):
        """helper function to get all pawn moves"""
        self._check_pawn_forward_move(row, col, moves)
        self._check_pawn_left_capture(row, col, moves)
        self._check_pawn_right_capture(row, col, moves)

    def _check_pawn_forward_move(self, row, col, moves):
        """helper function to check pawn's forward moves"""
        row_adder = -1 if self.white_to_move else 1
        row_direction, first_move_row_direction = row + row_adder, row + row_adder * 2
        base_row = 6 if self.white_to_move else 1
        if self.board[row_direction][col] == "--":  # 1 sq advance
            moves.append(Move((row, col), (row_direction, col), self.board))
            if (
                row == base_row and self.board[first_move_row_direction][col] == "--"
            ):  # 2-sq advance
                self._append_move((row, col), (first_move_row_direction, col), moves)

        return moves

    def _check_pawn_left_capture(self, row, col, moves):
        """helper function to check pawn's left diagonal moves"""
        enemy_color = self._get_enemy_color()
        row_direction = row + self._get_color_direction()
        if (col - 1) >= 0:  # safety check
            if self.board[row_direction][col - 1][0] == enemy_color:
                self._append_move((row, col), (row_direction, col - 1), moves)

        return moves

    def _check_pawn_right_capture(self, row, col, moves):
        """helper function to check pawn's right diagonal moves"""
        enemy_color = self._get_enemy_color()
        row_direction = row + self._get_color_direction()
        if (col + 1) <= 7:  # safety check
            if self.board[row_direction][col + 1][0] == enemy_color:
                self._append_move((row, col), (row_direction, col + 1), moves)

        return moves

    def _get_rook_moves(self, row, col, moves):
        """helper function to get all rook moves"""
        enemy_color = self._get_enemy_color()
        for direction in self.rook_directions:
            # for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if self._is_on_board(end_row, end_col):  # square is on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--" or end_piece[0] == enemy_color:
                        self._append_move((row, col), (end_row, end_col), moves)
                        if end_piece[0] == enemy_color:
                            break  # cannot move beyond another piece
                    else:
                        break  # same color piece
                else:
                    break  # square is off board

    def _get_knight_moves(self, row, col, moves):
        """helper function to get all knight moves"""
        for move in self.knight_moves:
            end_row = row + move[0]
            end_col = col + move[1]
            if self._is_on_board(end_row, end_col):
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != self._get_player_color():
                    self._append_move((row, col), (end_row, end_col), moves)

    def _get_bishop_moves(self, row, col, moves):
        """helper function to get all bishop moves"""
        enemy_color = self._get_enemy_color()
        for direction in self.bishop_directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if self._is_on_board(end_row, end_col):  # square is on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--" or end_piece[0] == enemy_color:
                        self._append_move((row, col), (end_row, end_col), moves)
                        if end_piece[0] == enemy_color:
                            break  # cannot move beyond another piece
                    else:
                        break  # same color piece
                else:
                    break  # square is off board

    def _get_queen_moves(self, row, col, moves):
        """helper function to get all queen moves"""
        self._get_rook_moves(row, col, moves)
        self._get_bishop_moves(row, col, moves)

    def _get_king_moves(self, row, col, moves):
        """helper function to get all king moves"""
        for row_move, col_move in self.king_moves:
            end_row = row + row_move
            end_col = col + col_move
            if self._is_on_board(end_row, end_col):
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != self._get_player_color():
                    self._append_move((row, col), (end_row, end_col), moves)


class Move:

    ranks_to_rows = dict([(str(i), j) for i, j in zip(range(1, 9), reversed(range(8)))])
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board):
        self.start_row, self.start_col = start_square
        self.end_row, self.end_col = end_square
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = (
            self.start_row * 1000
            + self.start_col * 100
            + self.end_row * 10
            + self.end_col
        )

    # ==============================================================
    # magic methods
    # ==============================================================

    def __eq__(self, other):
        """overriding equal method"""
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    # ==============================================================

    def get_chess_notation(self):
        return self._get_rank_file(self.start_row, self.start_col) + self._get_rank_file(
            self.end_row, self.end_col
        )

    def _get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]
