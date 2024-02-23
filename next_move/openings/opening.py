from pydantic import BaseModel
from datetime import datetime
from collections import defaultdict, Counter

import numpy as np


class Opening(BaseModel):
    fen: str
    eco: str
    name: str
    num_moves: int
    dates: list[datetime] = []
    results: list[float] = []
    occurrence: int = 0
    following_moves: Counter = Counter()
    following_game_scores: list[float] = []
    best_next_move: str = ""

    def __hash__(self):
        return hash(self.fen)

    def __eq__(self, other: "Opening"):
        return self.fen == other.fen

    def __repr__(self):
        return f"{self.eco} ({self.name}, {np.average(self.following_game_scores):.2f}, {np.average(self.results):.2f})"

    def __str__(self):
        return self.__repr__()

    def __add__(self, other: "Opening"):
        self.dates += other.dates
        self.results += other.results
        self.occurrence += other.occurrence
        self.following_moves = self.following_moves + other.following_moves
        self.following_game_scores += other.following_game_scores
        # TODO Stockfish is non-deterministic when running on multiple cores
        # assert self.best_next_move == other.best_next_move, "The best next move should be the same for the same FEN"
        return self

    def update_opening(
        self,
        date: datetime,
        result: float,
        following_move: str,
        score: float,
        best_move: str,
    ):
        self.following_moves[following_move] += 1
        self.dates.append(date)
        self.results.append(result)
        self.occurrence += 1
        self.following_game_scores.append(score)
        self.best_next_move = best_move
