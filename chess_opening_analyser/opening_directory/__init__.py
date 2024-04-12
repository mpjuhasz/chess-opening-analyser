import pandas as pd


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
        rows = self.openings[self.openings.fen == fen]
        if rows.shape[0] > 0:
            row = rows.to_dict(orient="records")[0]
            row["num_moves"] = len(row.get("moves", "").split(" "))
            row["index"] = rows.index.tolist()[
                0
            ]  # index from the DB, for uniqueness later in the UI
            return row
        else:
            return {}
