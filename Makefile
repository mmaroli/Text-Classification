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
	# sudo docker build --tag=ad-category-container .

shell:
	sudo docker exec -it "ad-category-container" bash
	# sudo docker run --runtime=nvidia --rm -it -v "${PWD}:/app" ad-category-container bash

down:
	@echo "Cleaning up..."
	sudo docker-compose down --remove-orphans
