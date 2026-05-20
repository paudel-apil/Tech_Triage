from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import tickets, dev
from app.core.config import settings
from app.db.models import Base
from app.db.session import engine
import asyncio
from contextlib import asynccontextmanager
from app.db.session import SessionLocal

Base.metadata.create_all(bind = engine)


async def keep_db_alive():
    while True:
        try:
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
        except Exception:
            pass
        await asyncio.sleep(300)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(keep_db_alive())
    yield

    task.cancel()
    


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
app.include_router(dev.router, prefix = "/api/v1")

@app.get('/')
def root():
    return {'message': 'Tech Support Tickets Backend is running'}

