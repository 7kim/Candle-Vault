# Candle Vault Skill

This folder is an Anthropic-style skill for agents that need to configure and run Candle Vault for a user.

## Install

Point your agent at this folder:

```text
skills/candle-vault/
```

The required file is `SKILL.md`. It contains the skill metadata and the agent instructions.

## Use

Ask the agent something like:

```text
Install and use the Candle Vault skill from skills/candle-vault, then configure this repo and fetch BTC/USDT and SOL/USDT 1h candles since 2024-06-01.
```

The agent should read the repo, ask the missing `config.toml` questions, update `config.toml`, run `uv sync`, smoke-check the CLI, and then run the fetch command.

## ccxt reference

Before changing ccxt-related code or troubleshooting exchange behavior, the agent should prefer current ccxt references over guessing.

- Local Python introspection is useful when available, for example `python -c "import ccxt; help(ccxt)"`.
- `python -m ccxt --help` is not expected to work because ccxt is a Python package, not a CLI module.
- If local help is not enough, read the ccxt docs and the LLM reference at <https://github.com/ccxt/ccxt/blob/master/llms.txt>.

## Notes

- Candle Vault writes CSV files only; it does not place trades.
- Market data fetching requires internet access.
- Generated `Candle_Data/` output should stay out of git.
