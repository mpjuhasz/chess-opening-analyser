.PHONY: install test

install:
	poetry install
	poetry run pre-commit install
	poetry run ipython kernel install --user

test:
	poetry run python -m pytest -vvv

analyse:
	poetry run python cli/analyse_openings.py --player-id $(player-id)

vis:
	poetry run streamlit run streamlit/analyse.py
