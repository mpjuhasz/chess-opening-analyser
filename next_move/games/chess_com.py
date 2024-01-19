import requests
from next_move.games import GameRetriever
from itertools import chain


class ChessCom(GameRetriever):
    """Chess.com game retriever responsible for retrieving games from chess.com"""

    GAMES_EXT = "games/archives"
    ARCHIVE_URL = "https://api.chess.com/pub/player"

    def _get_games(self, player_id: str, months: list[str] = None) -> list[str]:
        if months is None:
            months = []

        monthly_urls = self._get_monthly_archive(player_id)

        if months:
            monthly_urls = [url for url in monthly_urls if url[-7:] in months]

        return list(
            chain.from_iterable(self._get_games_in_month(url) for url in monthly_urls)
        )

    def _get_monthly_archive(self, player_id: str) -> list[str]:
        monthly_urls = requests.get(f"{self.ARCHIVE_URL}/{player_id}/{self.GAMES_EXT}")
        return monthly_urls.json().get("archives", [])

    @staticmethod
    def _get_games_in_month(url: str) -> list[str]:
        monthly_archive = requests.get(url).json()
        return [game.get("pgn", "") for game in monthly_archive.get("games", [])]
