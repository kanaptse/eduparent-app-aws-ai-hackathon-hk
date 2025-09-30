from mangum import Mangum
from app.main import app
from app.db.database import engine, Base
from app.models.user import User  # Import to register with Base

# Create tables on Lambda initialization
Base.metadata.create_all(bind=engine)

# Lambda handler
handler = Mangum(app, lifespan="off")