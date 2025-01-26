.venv:
	@python3 -m venv .venv
	@. .venv/bin/activate && npm install --legacy-peer-deps > /dev/null; 


run: .venv
	@(. .venv/bin/activate; \
		npm run dev;)
