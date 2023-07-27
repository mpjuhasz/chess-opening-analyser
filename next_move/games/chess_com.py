import requests
from next_move.games import GameProcessor


class ChessCom(GameProcessor):
    GAMES_EXT = 'games/archives'
    ARCHIVE_URL = 'https://api.chess.com/pub/player'

    def _get_game(self, url: str) -> list[str]:
        monthly_archive = requests.get(url).json()
        # TODO
        return [game.get("pgn", "") for game in monthly_archive.get("games", [])]

    def _get_archive(self, player_id: str, **kwargs) -> dict:
        games = requests.get(f"{self.ARCHIVE_URL}/{player_id}/{self.GAMES_EXT}")
        return games.json()


