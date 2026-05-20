from contextlib import asynccontextmanager
from typing import Annotated, Generic, TypeVar

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from sqlmodel import SQLModel, Session, select

from database import engine
from models import Campaign, CampaignCreate
from seed import seed_database


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():

    with Session(engine) as session:
        yield session


SessionDependency = Annotated[Session, Depends(get_session)]


T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    data: T


@asynccontextmanager
async def lifespan(app: FastAPI):

    create_db_and_tables()

    seed_database()

    yield


app = FastAPI(
    root_path="/api/v1",
    lifespan=lifespan
)


@app.get("/campaigns", response_model=Response[list[Campaign]])
async def read_campaigns(session: SessionDependency):

    data = session.exec(select(Campaign)).all()

    return {"data": data}


@app.get("/campaigns/{id}", response_model=Response[Campaign])
async def read_campaign(id: int, session: SessionDependency):

    data = session.get(Campaign, id)

    if not data:
        raise HTTPException(status_code=404)

    return {"data": data}