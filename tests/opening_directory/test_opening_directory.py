from next_move.opening_directory import EcoDB


def test_eco_db():
    db_path = "eco/openings.json"

    eco_db = EcoDB(db_path)

    opening = eco_db.lookup("rn1qkbnr/pp2pppp/2p5/5b2/3PN3/8/PPP2PPP/R1BQKBNR w KQkq -")

    assert opening["eco"] == "B18"
    assert opening["name"] == "Caro-Kann Defense: Classical Variation"
    assert opening["moves"] == "e2e4 c7c6 d2d4 d7d5 b1d2 d5e4 d2e4 c8f5"
