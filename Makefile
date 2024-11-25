build-container:
	docker build -t ms-wb .

start-dev-container:
	docker run --network=host --env-file .env --rm -p 8080:8080 ms-wb

start:
	poetry run python main.py

build-dev:
	docker compose -f docker-compose.dev.yml build

build:
	docker compose -f docker-compose.yml build

up-dev:
	docker compose -f docker-compose.dev.yml up

up:
	docker compose -f docker-compose.yml up
