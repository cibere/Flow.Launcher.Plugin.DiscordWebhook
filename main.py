from pathlib import Path
import sys

root = Path(__file__).parent
sys.path.extend(
    str(p) for p in (root, root / "lib", root / ".venv" / "lib" / "site-packages")
)

from plugin.core import plugin

plugin.run()
