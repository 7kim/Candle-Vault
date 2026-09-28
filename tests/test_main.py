import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from main import FetchConfig, output_path, rows_from_ohlcv


class FetcherTest(TestCase):
    def test_config_and_csv_rows(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.toml"
            config_file.write_text(
                """
[fetch]
exchange = "binance"
symbols = ["BTC/USDT"]
timeframes = ["1h"]
since = "2024-06-01T00:00:00Z"
output_dir = "data"
""".strip()
            )

            config = FetchConfig.from_file(config_file)
            default_config_file = Path(temp_dir) / "default-config.toml"
            default_config_file.write_text(
                """
[fetch]
symbols = ["BTC/USDT"]
timeframes = ["1h"]
since = "2024-06-01T00:00:00Z"
""".strip()
            )
            default_config = FetchConfig.from_file(default_config_file)

        rows = rows_from_ohlcv([[1717200000000, 1, 2, 0.5, 1.5, 10]])

        self.assertEqual(config.symbols, ("BTC/USDT",))
        self.assertEqual(default_config.output_dir, Path("Candle_Data"))
        self.assertEqual(rows[0]["date"], "2024-06-01")
        self.assertEqual(output_path(Path("data"), "BTC/USDT", "1h").name, "BTC_USDT_1h.csv")
