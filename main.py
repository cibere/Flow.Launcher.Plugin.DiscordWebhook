import sys
from pathlib import Path

root = Path(__file__).parent
sys.path.extend(
    str(p) for p in (root, root / "lib", root / ".venv" / "lib" / "site-packages")
)

from discordwebhook.core import plugin  # noqa: E402

plugin.run()
