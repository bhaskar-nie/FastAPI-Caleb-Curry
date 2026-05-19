from fastapi import FastAPI
from datetime import datetime
from typing import Any
from fastapi import HTTPException, Response
from random import randint

app = FastAPI(root_path="/api/v1")


@app.get("/")
async def root():
    return {"message": "This is FastAPI course by Caleb Curry"}


data: Any = [
    {
        "campaign_id": 1,
        "name": "Summer Launch",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    },
    {
        "campaign_id": 2,
        "name": "Rainy Launch",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    },
    {
        "campaign_id": 3,
        "name": "Winter Launch",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    }
]


@app.get("/campaigns")
async def read_campaigns():
    return {
        "campaigns": data
    }


@app.get("/campaigns/{id}")
async def read_campaign(id: int):

    for campaign in data:

        if campaign.get("campaign_id") == id:
            return campaign

    raise HTTPException(status_code=404)


@app.post("/campaigns")
async def add_campaign(body: dict[str, Any]):

    new_campaign: Any = {
        "campaign_id": randint(100, 1000),
        "name": body.get("name"),
        "due_date": body.get("due_date"),
        "created_at": body.get("created_at")
    }

    data.append(new_campaign)

    return {"new_campaign": new_campaign}


@app.put("/campaigns/{id}")
async def update_campaign(id: int, body: dict[str, Any]):

    for index, campaign in enumerate(data):

        if campaign.get("campaign_id") == id:

            updated_campaign: Any = {
                "campaign_id": id,
                "name": body.get("name"),
                "due_date": body.get("due_date"),
                "created_at": campaign.get("created_at")
            }

            data[index] = updated_campaign

            return {"campaign": updated_campaign}

    raise HTTPException(status_code=404)


@app.delete("/campaigns/{id}")
async def delete_campaign(id: int):

    for index, campaign in enumerate(data):

        if campaign.get("campaign_id") == id:

            data.pop(index)

            return Response(status_code=204)

    raise HTTPException(status_code=404)


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