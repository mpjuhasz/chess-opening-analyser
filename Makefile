.PHONY: install test

install:
	poetry install
	poetry run pre-commit install
	poetry run ipython kernel install --user

test:
	poetry run python -m pytest -vvv

vis:
	poetry run streamlit run app/streamlit_app.py
