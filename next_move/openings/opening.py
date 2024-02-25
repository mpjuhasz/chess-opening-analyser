from pydantic import BaseModel
from datetime import datetime
from collections import defaultdict, Counter

import numpy as np

from next_move.games import PlayerColour


class Opening(BaseModel):
    fen: str
    eco: str
    name: str
    num_moves: int
    colour: list[PlayerColour] = []
    dates: list[datetime] = []
    results: list[float] = []
    occurrence: int = 0
    following_moves: list[str] = []
    following_game_scores: list[float] = []
    # score_in_five_moves = list[float] = []  TODO this is to be added
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
        self.colour += other.colour
        # TODO Stockfish is non-deterministic when running on multiple cores
        # assert self.best_next_move == other.best_next_move, "The best next move should be the same for the same FEN"
        return self

    def partition_by_colour(self, colour: PlayerColour) -> "Opening":
        """Partitions the opening by colour"""
        indices = [i for i, c in enumerate(self.colour) if c == colour]
        return Opening(
            fen=self.fen,
            eco=self.eco,
            name=self.name,
            num_moves=self.num_moves,
            colour=[self.colour[i] for i in indices],
            dates=[self.dates[i] for i in indices],
            results=[self.results[i] for i in indices],
            occurrence=len(indices),
            following_moves=[self.following_moves[i] for i in indices],
            following_game_scores=[self.following_game_scores[i] for i in indices],
            best_next_move=self.best_next_move,
        )

    def update_opening(
        self,
        colour: PlayerColour,
        date: datetime,
        result: float,
        following_move: str,
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
