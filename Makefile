up:
	@bash -c 'set -a; [ -f .env ] && . .env; set +a; docker-compose up --build -d'

down:
	@bash -c 'set -a; [ -f .env ] && . .env; set +a; docker-compose down'

restart:
	@bash -c 'set -a; [ -f .env ] && . .env; set +a; docker-compose down && docker-compose up --build'

logs:
	@bash -c 'set -a; [ -f .env ] && . .env; set +a; docker-compose logs -f'

ps:
	@bash -c 'set -a; [ -f .env ] && . .env; set +a; docker-compose ps'

cleanup:
	@bash -c 'set -a; [ -f .env ] && . .env; set +a; docker-compose down --rmi all --volumes --remove-orphans' 