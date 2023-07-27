from abc import ABC, abstractmethod
from pathlib import Path
import json
from tqdm import tqdm


class GameProcessor(ABC):
    CACHE_DIR = Path("next_move/cache")

    def __init__(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def _get_game(self, *args, **kwargs) -> str:
        """Returns a single game from the platform in PGN format"""

    @abstractmethod
    def _get_archive(self, player_id: str, **kwargs) -> dict:
        """Returns the game archive for a player with dates"""

    def _load_from_cache(self, player_id: str) -> list[str]:
        with open(self.CACHE_DIR / f"{player_id}.json", 'r', encoding='utf-8') as f:
            games = json.load(f)
        return games

    def _cache_games(self, player_id: str, games: list[str]):
        with open(self.CACHE_DIR / f"{player_id}.json", 'w', encoding='utf-8') as f:
            json.dump(games, f, ensure_ascii=False, indent=4)

    def get_all_games(self, player_id: str):
        if Path(self.CACHE_DIR / f"{player_id}.json").exists():
            games = self._load_from_cache(player_id)
        else:
            archive = self._get_archive(player_id)

            games = []
            for req_url in tqdm(archive.items()):
                games += self._get_game(req_url)
            self._cache_games(player_id, games)
        return games

