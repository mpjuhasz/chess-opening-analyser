from abc import ABC, abstractmethod
from pathlib import Path
import json
from tqdm import tqdm
from enum import Enum
from typing import Optional


class PlayerColour(str, Enum):
    W = "White"
    B = "Black"


class GameRetriever(ABC):
    CACHE_DIR = Path("next_move/cache")

    def __init__(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def _get_games(
        self, player_id: str, months: Optional[list[str]] = None
    ) -> list[str]:
        """Returns a single game from the platform in PGN format"""
        raise NotImplementedError

    def _load_from_cache(self, player_id: str) -> list[str]:
        with open(self.CACHE_DIR / f"{player_id}.json", "r", encoding="utf-8") as f:
            games = json.load(f)
        return games

    def _cache_games(self, player_id: str, games: list[str]):
        with open(self.CACHE_DIR / f"{player_id}.json", "w", encoding="utf-8") as f:
            json.dump(games, f, ensure_ascii=False, indent=4)

    def get_all_games(self, player_id: str, caching=True) -> list[str]:
        """Gets all the games for the given player_id in the PGN format"""
        if Path(self.CACHE_DIR / f"{player_id}.json").exists() and caching:
            games = self._load_from_cache(player_id)
        else:
            games = self._get_games(player_id)
            if caching:
                self._cache_games(player_id, games)
        return games
