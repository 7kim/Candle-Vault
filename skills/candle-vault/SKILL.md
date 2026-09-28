---
name: candle-vault
description: Configure and run the Candle Vault crypto OHLCV fetcher. Use when the user wants an agent to install, configure, run, schedule, troubleshoot, or explain this repo's CSV candle-data workflow.
---

# Candle Vault

Use this skill to help a user operate Candle Vault, a small Python/uv CLI that fetches crypto OHLCV candles through `ccxt` and writes CSV files.

## Workflow

1. Locate the Candle Vault repo and read `README.md`, `config.toml`, `pyproject.toml`, and `src/main.py` before changing anything.
2. Confirm `uv` is available with `uv --version`. If it is missing, ask before installing it.
3. Install dependencies from the repo root with `uv sync`.
4. Ask the user only the `config.toml` questions needed for the run.
5. Edit `config.toml` with the user's answers.
6. Smoke-check with `uv run main.py --help`.
7. Run once with `uv run main.py --config config.toml`, unless the user asks for a repeating schedule.

## Config Questions

Ask these in plain language and keep the user's answers visible before editing `config.toml`:

- `exchange`: Which ccxt exchange id should be used? Default to `binance` when the user has no preference.
- `symbols`: Which trading pairs should be fetched? Use ccxt pair format such as `BTC/USDT`, `ETH/USDT`, or `SOL/USDT`.
- `timeframes`: Which candle intervals should be fetched? Common Binance intervals include `1m`, `5m`, `15m`, `1h`, `4h`, `12h`, and `1d`.
- `since`: What UTC start timestamp should be used? Store it as ISO-8601, for example `2024-06-01T00:00:00Z`.
- `output_dir`: Where should CSV files be written? Default to `Candle_Data`.

Do not invent symbols, timeframes, dates, or exchange ids for the user. Sensible defaults are fine only after naming them and getting enough user agreement to proceed.

## Running

Run once:

```bash
uv run main.py --config config.toml
```

Run repeatedly every N hours only when requested:

```bash
uv run main.py --config config.toml --every-hours 1
```

Generated CSV files are written under:

```text
{output_dir}/{BASE_SYMBOL}/{RUN_DATE}/{SYMBOL}_{TIMEFRAME}.csv
```

## ccxt Reference

Before changing ccxt-related code or troubleshooting exchange behavior, prefer current ccxt references over guessing:

- Use local Python introspection when available, for example `python -c "import ccxt; help(ccxt)"`.
- Do not rely on `python -m ccxt --help`; ccxt is a Python package and is not expected to provide a CLI `__main__`.
- If local help is not enough, read the ccxt docs and `https://github.com/ccxt/ccxt/blob/master/llms.txt`.

## Guardrails

- This project fetches market data only. It does not place trades.
- Fetching requires internet access and may fail because of exchange limits, unsupported pairs, unsupported intervals, or regional restrictions.
- Do not commit generated `Candle_Data/` output.
- Before deleting generated data or changing an existing configured setup, show the exact path or config change and get user approval.
- For development changes, run `PYTHONPATH=src uv run python -m unittest discover -s tests` before reporting success.
