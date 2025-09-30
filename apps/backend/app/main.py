from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import feed, calculator, survey, card_stack, users, roleplay
from app.db.database import engine, Base
from app.models.user import User  


app = FastAPI(
    title="EduParent API",
    description="Cross-platform education companion API for parents with interactive card stacks",
    version="1.1.0",
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

# CORS middleware for Flutter frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",  # Flutter development server
        "http://127.0.0.1:8080",  # Flutter development server (alternative)
        "http://eduparent-frontend-web.s3-website-ap-northeast-1.amazonaws.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(feed.router, prefix="/api/feed", tags=["feed"])
app.include_router(card_stack.router, prefix="/api/card-stacks", tags=["card-stacks"])
app.include_router(calculator.router, prefix="/api/calculator", tags=["calculator"])
app.include_router(survey.router, prefix="/api/survey", tags=["survey"])
app.include_router(roleplay.router, prefix="/api/roleplay", tags=["roleplay"])

@app.get("/")
async def root():
    return {"message": "EduParent API with Card Stacks", "status": "running", "version": "1.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}