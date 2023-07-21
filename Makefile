.PHONY: install test lint check run 

help:
	@echo "install - install dependencies with poetry"
	@echo "lint - run linter and checks"


lint:
	./linter.sh
	
install:
	poetry install --no-root
	poetry shell

filetree_metadata_extraction: 
	python -m src.main