Testing Locally (recommended before pushing)

If you see platform errors like "Websocket error" or "An unknown error has occurred", reproduce and debug locally first:

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

2. Run the built-in test harness:

```powershell
python run_tests.py
```

What the tests cover:
- Starts an aiohttp instance using the same `stream_routes` used in production and hits `/` to validate the health JSON.
- Ensures `/favicon.ico` returns 404 to avoid noisy errors from platforms probing for a favicon or using websocket health checks.

If tests fail, run `pytest -q tests -k <pattern>` for a focused run and inspect the traceback. Fixes are easier to validate locally than debugging remote platform logs.

If you prefer manual checks, start the bot locally (with a valid `.env`) and curl the root endpoint:

```powershell
curl http://127.0.0.1:8000/
```

If the response is valid JSON and the bot client started (look for startup prints in logs), your health checks should pass on Koyeb/Heroku.
