from mangum import Mangum
from apps.backend.app.main import app

# Lambda handler
handler = Mangum(app, lifespan="off")