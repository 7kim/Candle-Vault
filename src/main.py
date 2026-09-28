from __future__ import annotations

import argparse
import csv
import time
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

import ccxt


CSV_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume", "date", "time")


@dataclass(frozen=True)
class FetchConfig:
    """User-editable settings loaded from config.toml."""

    exchange: str
    symbols: tuple[str, ...]
    timeframes: tuple[str, ...]
    since: str
    output_dir: Path

    @classmethod
    def from_file(cls, path: Path) -> "FetchConfig":
        data = tomllib.loads(path.read_text())
        fetch = data.get("fetch", {})
        config = cls(
            exchange=str(fetch.get("exchange", "binance")),
            symbols=tuple(fetch.get("symbols", ())),
            timeframes=tuple(fetch.get("timeframes", ())),
            since=str(fetch["since"]),
            output_dir=Path(fetch.get("output_dir", "crypto_data")),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if not self.symbols:
            raise ValueError("config must include at least one symbol")
        if not self.timeframes:
            raise ValueError("config must include at least one timeframe")


def get_exchange(exchange_id: str):
    try:
        exchange_class = getattr(ccxt, exchange_id)
    except AttributeError as error:
        raise ValueError(f"ccxt exchange not found: {exchange_id}") from error
    return exchange_class()


def iso_from_milliseconds(value: int) -> tuple[str, str, str]:
    timestamp = datetime.fromtimestamp(value / 1000, tz=UTC)
    return timestamp.isoformat(), timestamp.date().isoformat(), timestamp.time().isoformat()


def rows_from_ohlcv(ohlcv: Iterable[list[float]]) -> list[dict[str, object]]:
    """Convert ccxt OHLCV rows into CSV-friendly dictionaries."""

    rows = []
    for timestamp_ms, open_, high, low, close, volume in ohlcv:
        timestamp, date, time_ = iso_from_milliseconds(int(timestamp_ms))
        rows.append(
            {
                "timestamp": timestamp,
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
                "date": date,
                "time": time_,
            }
        )
    return rows


def output_path(output_dir: Path, symbol: str, timeframe: str, today: datetime | None = None) -> Path:
    """Keep generated data grouped by base coin and fetch date."""

    run_date = (today or datetime.now(UTC)).date().isoformat()
    base_symbol = symbol.split("/", 1)[0]
    filename = f"{symbol.replace('/', '_')}_{timeframe}.csv"
    return output_dir / base_symbol / run_date / filename


def save_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def fetch_all(config: FetchConfig) -> list[Path]:
    exchange = get_exchange(config.exchange)
    since = exchange.parse8601(config.since)
    written = []

    for symbol in config.symbols:
        for timeframe in config.timeframes:
            rows = rows_from_ohlcv(exchange.fetch_ohlcv(symbol, timeframe, since))
            path = output_path(config.output_dir, symbol, timeframe)
            save_csv(path, rows)
            written.append(path)
            print(f"saved {symbol} {timeframe} -> {path}")

    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch OHLCV candles to CSV files.")
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    parser.add_argument("--every-hours", type=float, help="repeat the fetch every N hours")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = FetchConfig.from_file(args.config)

    while True:
        fetch_all(config)
        if not args.every_hours:
            return 0
        time.sleep(args.every_hours * 60 * 60)
