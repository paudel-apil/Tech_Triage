from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import tickets
from app.core.config import settings
from app.db.models import Base
from app.db.session import engine

Base.metadata.create_all(bind = engine)


app = FastAPI(
    title = settings.PROJECT_NAME,
    redirect_slashes = True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000",
                     "http://localhost:8000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


app.include_router(tickets.router, prefix = '/api/v1', tags = ['tickets'])

@app.get('/')
def root():
    return {'message': 'Tech Support Tickets Backend is running'}