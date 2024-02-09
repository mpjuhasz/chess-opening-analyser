import pandas as pd
from logger import logger


class EcoDB:
    """Database of eco openings"""
    def __init__(self, db_path: str):
        self.openings = pd.read_json(db_path)

    def lookup(self, fen: str) -> dict:
        """
        Looks up the fen in the database, and returns the ECO, name, moves and number of moves

        Args:
            fen (str): fen encoding of the board

        Returns:
            row (dict): in the format of:
            {
                "eco": str,
                "name": str,
                "fen": str,
                "moves": str,
                "num_moves": int,
            }
        """
        rows = self.openings[self.openings.fen == fen].to_dict(orient='records')
        if rows:
            row = rows[0]
            row['num_moves'] = len(row.get('moves', '').split(' '))
            return row
        else:
            return {}


