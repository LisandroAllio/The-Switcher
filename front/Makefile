.venv:
	@python3 -m venv .venv
	@ (. .venv/bin/activate; \
	npm install;)

run: .venv
	@(. .venv/bin/activate; \
		npm run dev;)
