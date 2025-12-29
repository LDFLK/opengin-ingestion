
# Default port for dev server
PORT ?= 3001

.PHONY: install build run-dev start clean

install:
	npm install

build:
	npm run build

run-dev:
	npm run dev -- -p $(PORT)

start:
	npm run start -- -p $(PORT)

clean:
	rm -rf .next out
