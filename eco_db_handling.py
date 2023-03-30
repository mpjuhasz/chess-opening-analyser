import pandas as pd
from logger import logger


def build_eco_db() -> pd.DataFrame:
    openings = pd.read_json("./eco/openings.json")
    logger.info(f"Loaded eco data: {len(openings)}")
    return openings


def eco_lookup(fen: str, eco_db: pd.DataFrame) -> dict:
    """
    Looks up the fen in the database, and returns the ECO, name, moves and number of moves

    Args:
        fen (str): fen encoding of the board
        eco_db (pd.DataFrame): database of eco openings

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
    rows = eco_db[eco_db.fen == fen].to_dict(orient='records')
    if rows:
        row = rows[0]
        row['num_moves'] = len(row.get('moves', '').split(' '))
        return row
    else:
        return {}


