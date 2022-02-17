"""Stares all information about current state of chess game. Determines valid moves of current state and keeps move log."""


class GameState:
    def __init__(self):
        # more efficient implementation would be with numpy
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

    def make_move(self, move):
        """executes move (does not work for castling, pawn promotion and en-passant"""
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

    def undo_move(self):
        """undo last move"""
        assert self.move_log

        move = self.move_log.pop()
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured
        self.white_to_move = not self.white_to_move

    def get_valid_moves(self):
        """all moves considering checks/rules"""
        return self.get_all_possible_moves()

    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if self._is_white_turn(turn) or self._is_black_turn(turn):
                    piece = self.board[row][col][1]
                    self.move_functions[piece](row, col, moves)

        return moves

    def _is_white_turn(self, turn):
        return turn == "w" and self.white_to_move

    def _is_black_turn(self, turn):
        return turn == "b" and not self.white_to_move

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
                moves.append(
                    Move((row, col), (first_move_row_direction, col), self.board)
                )

        return moves

    def _check_pawn_left_capture(self, row, col, moves):
        """helper function to check pawn's left diagonal moves"""
        row_direction, color = (row - 1, "b") if self.white_to_move else (row + 1, "w")
        if (col - 1) >= 0:  # captures to left
            if self.board[row_direction][col - 1][0] == color:
                moves.append(Move((row, col), (row_direction, col - 1), self.board))

        return moves

    def _check_pawn_right_capture(self, row, col, moves):
        """helper function to check pawn's right diagonal moves"""
        row_direction, color = (row - 1, "b") if self.white_to_move else (row + 1, "w")
        if (col + 1) <= 7:  # captures to right
            if self.board[row_direction][col + 1][0] == color:
                moves.append(Move((row, col), (row_direction, col + 1), self.board))

        return moves

    def _get_rook_moves(self, row, col, moves):
        """helper function to get all rook moves"""
        pass

    def _get_knight_moves(self, row, col, moves):
        """helper function to get all knight moves"""
        pass

    def _get_bishop_moves(self, row, col, moves):
        """helper function to get all bishop moves"""
        pass

    def _get_queen_moves(self, row, col, moves):
        """helper function to get all queen moves"""
        pass

    def _get_king_moves(self, row, col, moves):
        """helper function to get all king moves"""
        pass


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

    def __eq__(self, other):
        """overriding equal method"""
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        return self._get_rank_file(self.start_row, self.start_col) + self._get_rank_file(
            self.end_row, self.end_col
        )

    def _get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]
