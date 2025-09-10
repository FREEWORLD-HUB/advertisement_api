from fastapi import FastAPI, Form,File, UploadFile, HTTPException,status
from db import adverts_collection
from pydantic import BaseModel
from bson.objectid import ObjectId
from utils import replace_mongo_id
from typing import Annotated
import cloudinary
import cloudinary.uploader
import cloudinary.api

app = FastAPI()

# create a class to model the data
class Advert(BaseModel):
    title: str
    description: str
    price: float
    category: str
    
# configure cloudinary
cloudinary.config(
    cloud_name="dhqwkwo8e",
    api_key="544878511352217",
    api_secret="DB2whHclPE2tpDECsKPQNRq7G0Y"

)

@app.get("/")
def get_home():
    return {"message": "you are on the home page"}

@app.get("/adverts")
def get_adverts(title="", description="", limit=10, skip=0):
    # get all events from the database
    events = adverts_collection.find(
        filter={
            "$or": [
                {"title": {"$regex": title, "$options": "i"}},
                {"description": {"$regex": description, "$options": "i"}},
            ]
        },
        limit=int(limit),
        skip=int(skip)
    ).to_list()
    # returns response
    return {"data": list(map(replace_mongo_id, events))}


@app.post("/adverts")
def post_advert(
    title: Annotated[str, Form()], 
    description: Annotated[str, Form()],
    price: Annotated[float, Form()],
    category: Annotated[str, Form()],
    flyer: Annotated[UploadFile, File()]):
    # upload flyer to cloudinary
    upload_result = cloudinary.uploader.upload(flyer.file)
    # print(upload_result)  # Debugging line to check upload result
    # insert the event into the database
    adverts_collection.insert_one({
        "title": title,
        "description": description,
        "price": price,
        "category": category,
        "flyer_url": upload_result["secure_url"]
    })
    # events_collection.insert_one(event.model_dump())
    return {"message": "Advert added successfully"}
