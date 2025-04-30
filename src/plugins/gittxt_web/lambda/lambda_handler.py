from mangum import Mangum
from gittxt_web.main import app     # nothing under  “plugins” any more
handler = Mangum(app)
