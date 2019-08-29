.DEFAULT_GOAL := default

.PHONY = all default build run clean

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(patsubst %/,%,$(dir $(mkfile_path)))

all: default build shell down

default:
	@echo "Please select a command: make build, make run, make clean."

build:
	@echo "Building ad-category container..."
	sudo docker-compose up --build -d

shell:
	sudo docker exec -it "ad-category-predictor-container" bash

run:
	rm -r logs && mkdir logs
	sudo docker exec -it "ad-category-predictor-container" gunicorn --access-logfile logs/gunicorn-access.log --error-logfile logs/gunicorn-error.log --bind 0.0.0.0:5000 wsgi

down:
	@echo "Cleaning up..."
	sudo docker-compose down --remove-orphans
