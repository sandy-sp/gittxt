"""
Lambda entry-point for gittxt_web.
Creates a dummy top-level `plugins` package so that
`plugins.gittxt_web.*` imports resolve even though only
gittxt_web is bundled.
"""

import sys, types, importlib, pathlib
from mangum import Mangum

# 1️⃣  Add /var/task (the Lambda root) to sys.path
ROOT = pathlib.Path(__file__).resolve().parents[1]   # => /var/task
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 2️⃣  Make a fake `plugins` module if it doesn't exist
if "plugins" not in sys.modules:
    plugins_pkg = types.ModuleType("plugins")
    sys.modules["plugins"] = plugins_pkg
else:
    plugins_pkg = sys.modules["plugins"]

# 3️⃣  Import gittxt_web and attach it under plugins
if not hasattr(plugins_pkg, "gittxt_web"):
    plugins_pkg.gittxt_web = importlib.import_module("gittxt_web")

# 4️⃣  Now the normal import works
from plugins.gittxt_web.main import app   # noqa: E402

handler = Mangum(app)
