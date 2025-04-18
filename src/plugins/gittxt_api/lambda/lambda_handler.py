from mangum import Mangum
from plugins.gittxt_api.main import app

handler = Mangum(app)
