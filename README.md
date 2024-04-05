# next-move

This a library meant for the analysis and visualisation of a users chess games.

Currently supported chess platforms:
* chess.com

 Currently supported engines:
* Stockfish

## Setup
The analyser uses a chess analysis engine. Download Stockfish, and set the environment variable `STOCKFISH_DIR` to the directory containing it.

```bash
$ make install
```

## Running the streamlit app

There's a streamlit app with a simple UI that helps with interacting with the openings data.

```bash
make vis
```

## Running the analysis CLI
The analysis pipeline can also be run as a CLI tool to analyse all the games of a user.

```bash
make analyse --player-id <PLAYER_ID>
```

The results are saved locally in `tree.json`, which is the `Tree` object persisted to disk.
