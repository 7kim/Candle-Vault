from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).with_name("src")))

from main import main  # noqa: E402


raise SystemExit(main())
