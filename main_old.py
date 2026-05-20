from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from datetime import datetime, timezone
from typing import Annotated, Any, Generic, TypeVar
from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Session, create_engine, select # not from sqlalchemy

from seed import seed_database

class Campaign(SQLModel, table=True):

    campaign_id: int | None = Field(default=None, primary_key=True)

    name: str = Field(index=True)

    due_date: datetime | None = Field(default=None, index=True)

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=True,
        index=True
    ) # Set at application/database level

class CampaignCreate(SQLModel): # dont put table = true here
    name : str
    due_date : datetime | None = None

T =TypeVar("T")
class Response(BaseModel, Generic[T]):
    #campaigns : list[Campaign]
    data : T

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread" : False}
engine = create_engine(sqlite_url, connect_args = connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    # Use a context manager here
    with Session(engine) as session:
        yield session

SessionDependency  =  Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app : FastAPI):
    create_db_and_tables()
    # with Session(engine) as session: # This is a context manager that will automatically free any resources
    #     if not session.exec(select(Campaign)).first():
    #          # Similar to create table if not exists
    #          session.add_all([
    #              Campaign(name = "Summer Launch", due_date=datetime.now()),
    #              Campaign(name = "Black Friday", due_date=datetime.now())
    #          ])
    #          session.commit()
    seed_database()
    yield

app = FastAPI(root_path="/api/v1", lifespan = lifespan)


# @app.get("/")
# async def root():
#     return {"message": "This is FastAPI course by Caleb Curry"}


# data: Any = [
#     {
#         "campaign_id": 1,
#         "name": "Summer Launch",
#         "due_date": datetime.now(),
#         "created_at": datetime.now()
#     },
#     {
#         "campaign_id": 2,
#         "name": "Rainy Launch",
#         "due_date": datetime.now(),
#         "created_at": datetime.now()
#     },
#     {
#         "campaign_id": 3,
#         "name": "Winter Launch",
#         "due_date": datetime.now(),
#         "created_at": datetime.now()
#     }
# ]


# @app.get("/campaigns")
# async def read_campaigns():
#     return {
#         "campaigns": data
#     }


# @app.get("/campaigns/{id}")
# async def read_campaign(id: int):

#     for campaign in data:

#         if campaign.get("campaign_id") == id:
#             return campaign

#     raise HTTPException(status_code=404)


# @app.post("/campaigns")
# async def add_campaign(body: dict[str, Any]):

#     new_campaign: Any = {
#         "campaign_id": randint(100, 1000),
#         "name": body.get("name"),
#         "due_date": body.get("due_date"),
#         "created_at": body.get("created_at")
#     }

#     data.append(new_campaign)

#     return {"new_campaign": new_campaign}


# @app.put("/campaigns/{id}")
# async def update_campaign(id: int, body: dict[str, Any]):

#     for index, campaign in enumerate(data):

#         if campaign.get("campaign_id") == id:

#             updated_campaign: Any = {
#                 "campaign_id": id,
#                 "name": body.get("name"),
#                 "due_date": body.get("due_date"),
#                 "created_at": campaign.get("created_at")
#             }

#             data[index] = updated_campaign

#             return {"campaign": updated_campaign}

#     raise HTTPException(status_code=404)


# @app.delete("/campaigns/{id}")
# async def delete_campaign(id: int):

#     for index, campaign in enumerate(data):

#         if campaign.get("campaign_id") == id:

#             data.pop(index)

#             return Response(status_code=204)

#     raise HTTPException(status_code=404)


# --------------------------------------------------
# Notes
# --------------------------------------------------

# We use `body: dict[str, Any]` because FastAPI automatically
# reads the JSON request body and converts it into a Python dictionary.

# `body`
# This variable stores the incoming JSON data.

# `dict[str, Any]`
# `dict` means the request body should be a dictionary (JSON object).
# `str` means the dictionary keys should be strings.
# `Any` means the values can be of any data type.

# Example accepted JSON:
#
# {
#     "name": "Summer Sale",
#     "due_date": "2026-06-01",
#     "created_at": "2026-05-19"
# }

# FastAPI automatically converts the JSON into a Python dictionary.

# This approach is cleaner and works better with FastAPI docs (`/docs`)
# and the Swagger UI Execute / Try it out button.

# FastAPI automatically generates:
#
# - Request body section
# - JSON editor
# - Execute button support
# - Basic validation hints

# Example auto-generated Swagger JSON:
#
# {
#   "additionalProp1": {}
# }

# We do NOT use `request: Request` here because that requires
# manually reading the request body using:
#
#     body = await request.json()

# Using `Request` gives full access to the HTTP request,
# but it bypasses some of FastAPI's automatic request body handling
# and documentation features.

# `Request` is mainly used when we need:
#
# - Request headers
# - Cookies
# - Client IP address
# - Uploaded files
# - Raw request body
# - Advanced request handling

# For normal JSON APIs,
# `body: dict[str, Any]` or a Pydantic model
# is the preferred FastAPI approach.

# `async`
# Makes the function asynchronous.
# FastAPI can handle other requests while waiting for
# database queries, API calls, file uploads, etc.

# --------------------------------------------------

#Based on Database
@app.get("/campaigns", response_model=Response[list[Campaign]])
async def read_campaigns(session : SessionDependency): # Input param is Session object
    data = session.exec(select(Campaign)).all() # session.exec() for multiple values
    return {"data" : data}

@app.get("/campaigns/{id}", response_model=Response[Campaign])
async def read_campaign(id : int, session : SessionDependency):
    data = session.get(Campaign, id) # session.get() for single value
    if not data:
        raise HTTPException(status_code=404)
    return {"data" : data}

@app.post("/campaigns", status_code=201, response_model=Response[Campaign])
async def create_campaign(campaign : CampaignCreate, session : SessionDependency): # CampaignCreate instead of Campaign
    #Issues caused
    # we dont want to add campaign_id and created_at, as these will be done server side
    # Create another type
    db_campaign = Campaign.model_validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)

    return {"data" : db_campaign}

@app.put("/campaigns/{campaign_id}", response_model=Response[Campaign])
async def update_campaign(
    campaign_id: int,
    campaign: CampaignCreate,
    session: SessionDependency
):

    data = session.get(Campaign, campaign_id)

    if not data:
        raise HTTPException(status_code=404)

    data.name = campaign.name
    data.due_date = campaign.due_date

    session.add(data)
    session.commit()
    session.refresh(data)

    return {"data": data}

@app.delete("/campaigns/{id}", status_code = 204)
async def delete_campaign(id:int, session: SessionDependency):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    session.delete(data)
    session.commit()
    