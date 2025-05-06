from mangum import Mangum
from gittxt_web.backend.main import app   
handler = Mangum(app)
