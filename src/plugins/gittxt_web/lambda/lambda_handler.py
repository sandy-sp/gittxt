from mangum import Mangum
from plugins.gittxt_web.main import app

handler = Mangum(app)
