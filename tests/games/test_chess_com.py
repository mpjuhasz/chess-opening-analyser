from next_move.games.chess_com import ChessCom
from chess import pgn
import io
from data_loader import load_game
from datetime import datetime, timedelta

# game attributes: 'parent', 'move', 'variations', 'comment', 'starting_comment', 'nags', 'headers', 'errors'


def test_chess_com(mocker):
    game_str = load_game()
    mocker.patch(
        "next_move.games.chess_com.ChessCom._get_games_in_month",
        return_value=[game_str]
    )
    mocker.patch(
        "next_move.games.chess_com.ChessCom._get_monthly_archive",
        return_value=["https://api.chess.com/pub/player/matyasj/games/2023/06"]
    )
    games_api = ChessCom()
    games = games_api._get_games("matyasj", months=["2023/06"])
    assert isinstance(games, list)
    assert isinstance(games[0], str)
    game = pgn.read_game(io.StringIO(games[0]))
    assert isinstance(game, pgn.Game)


def test_chess_com_2():
    games_api = ChessCom()
    start_time = datetime.now()
    games = games_api._get_games("matyasj", months=[f"2022/{m+1}" for m in range(12)])
    assert datetime.now() - start_time < timedelta(milliseconds=900)


def test_all_games(mocker):
    game_str = load_game()
    mocker.patch(
        "next_move.games.chess_com.ChessCom._get_games_in_month",
        return_value=[game_str]
    )
    mocker.patch(
        "next_move.games.chess_com.ChessCom._get_monthly_archive",
        return_value=["https://api.chess.com/pub/player/matyasj/games/2023/06"]
    )
    games_api = ChessCom()
    games = games_api.get_all_games("matyasj", caching=False)
    assert isinstance(games, list)
    assert isinstance(games[0], str)
    game = pgn.read_game(io.StringIO(games[0]))
    assert isinstance(game, pgn.Game)


def test_all_games_online():
    games_api = ChessCom()
    start_time = datetime.now()
    games = games_api.get_all_games("matyasj", caching=False)
    assert datetime.now() - start_time < timedelta(seconds=20)
    assert len(games) > 10000
