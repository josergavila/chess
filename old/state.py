import chess
import numpy as np


class State:
    def __init__(self, board=None):
        if board is None:
            self.board = chess.Board()
        else:
            self.board = board

    def serialize(self):
        assert self.board.is_valid()

        board_state = np.zeros(64, np.uint8)
        for i in range(64):
            piece = self.board.piece_at(i)
            if piece is not None:
                board_state[i] = {"p": 1, "n": 2, "b": 3, "r": 4, "q": 5, "k": 6, \
                                  "P": 9, "N": 10, "B": 11, "R": 12, "Q": 13, "K": 14}[piece.symbol()]

        if self.board.has_queenside_castling_rights(False):
            assert board_state[0] == 4
            board_state[0] = 7

        if self.board.has_kingside_castling_rights(False):
            assert board_state[7] == 4
            board_state[7] = 7

        if self.board.has_queenside_castling_rights(True):
            assert board_state[56] == 8+4
            board_state[56] = 8+7

        if self.board.has_kingside_castling_rights(True):
            assert board_state[63] == 8+4
            board_state[63] = 8+7

        if self.board.ep_square is not None:
            assert board_state[self.board.ep_square] == 0
            board_state[self.board.ep_square] = 8
        board_state = board_state.reshape(8, 8)

        state = np.zeros((5, 8, 8), np.uint8)

        # columns to binary
        breakpoint()
        state[0] = (board_state>>3)&1
        state[:, :, 1] = (board_state>>2)&1
        state[:, :, 2] = (board_state>>1)&1
        state[:, :, 3] = (board_state>>0)&1

        # 4th column -> who's turn it is
        state[:, :, 4] = self.board.turn * 1.0

        return state

    def edges(self):
        return list(self.board.generate_legal_moves())

    def value(self):
        # TODO: add neural net
        return 1


if __name__ == "__main__":

    s = State()
    print(s.edges())
