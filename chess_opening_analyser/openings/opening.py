from typing import Optional
from pydantic import BaseModel
from datetime import datetime

import numpy as np

from chess_opening_analyser.games import PlayerColour


class Opening(BaseModel):
    fen: str
    eco: str
    name: str
    index: int
    num_moves: int
    colour: list[PlayerColour] = []
    dates: list[datetime] = []
    results: list[float] = []
    occurrence: int = 0
    following_moves: list[Optional[str]] = []
    following_game_scores: list[float] = []
    score_in_n_moves: list[float] = []
    best_next_move: str = ""

    def __hash__(self):
        return hash(self.fen)

    def __eq__(self, other: "Opening"):
        return self.fen == other.fen

    def __repr__(self):
        return f"{self.eco} ({self.name}, {np.average(self.following_game_scores):.2f}, {np.average(self.results):.2f})"

    def __str__(self):
        return self.__repr__()

    def __add__(self, other: Optional["Opening"]) -> "Opening":
        if other is None:
            return self
        self.dates += other.dates
        self.results += other.results
        self.occurrence += other.occurrence
        self.following_moves = self.following_moves + other.following_moves
        self.following_game_scores += other.following_game_scores
        self.colour += other.colour
        self.score_in_n_moves += other.score_in_n_moves
        # TODO Stockfish is non-deterministic when running on multiple cores
        # assert self.best_next_move == other.best_next_move, "The best next move should be the same for the same FEN"
        return self

    def __radd__(self, other: Optional["Opening"]) -> "Opening":
        """This allows None + Opening to use Opening's __add__"""
        return self.__add__(other)

    def partition_by_colour(self, colour: PlayerColour) -> Optional["Opening"]:
        """Partitions the opening by colour"""
        indices = [i for i, c in enumerate(self.colour) if c == colour]

        if not indices:
            return None

        return Opening(
            fen=self.fen,
            eco=self.eco,
            name=self.name,
            index=self.index,
            num_moves=self.num_moves,
            colour=[self.colour[i] for i in indices],
            dates=[self.dates[i] for i in indices],
            results=[self.results[i] for i in indices],
            occurrence=len(indices),
            following_moves=[self.following_moves[i] for i in indices],
            following_game_scores=[self.following_game_scores[i] for i in indices],
            score_in_n_moves=[self.score_in_n_moves[i] for i in indices],
            best_next_move=self.best_next_move,
        )

    def update_opening(
        self,
        colour: PlayerColour,
        date: datetime,
        result: float,
        following_move: Optional[str],
        score: float,
        best_move: str,
    ):
        self.following_moves.append(following_move)
        self.colour.append(colour)
        self.dates.append(date)
        self.results.append(result)
        self.occurrence += 1
        self.following_game_scores.append(score)
        self.best_next_move = best_move
