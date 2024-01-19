from pydantic import BaseModel
from datetime import datetime
from collections import defaultdict, Counter


class Opening(BaseModel):
    fen: str
    eco: str
    dates: list[datetime] = []
    win_number: int = 0
    occurrence: int = 0
    following_moves: Counter = Counter()
    following_game_scores: list[float] = []

    def __hash__(self):
        return hash(self.fen)

    def __add__(self, other: "Opening"):
        self.dates += other.dates
        self.win_number += other.win_number
        self.occurrence += other.occurrence
        self.following_moves = self.following_moves + other.following_moves
        self.following_game_scores += other.following_game_scores
        return self

    def update_opening(
        self,
        date: datetime,
        win: bool | int,
        following_move: str,
        following_game_score: float,
    ):
        self.following_moves[following_move] += 1
        self.dates.append(date)
        self.win_number += int(win)
        self.occurrence += 1
        self.following_game_scores.append(following_game_score)
