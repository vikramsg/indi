.PHONY: install test lint check run 

help:
	@echo "install - install dependencies with poetry"
	@echo "lint - run linter and checks"


lint:
	./linter.sh
	
install:
	poetry install --no-root
	poetry shell

task2: 
	python -m src.task2 --file-name=data/commission_dataset.csv