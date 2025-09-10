from fastapi import FastAPI, Form,File, UploadFile, HTTPException,status
from db import adverts_collection
from pydantic import BaseModel
from bson.objectid import ObjectId
from utils import replace_mongo_id
from typing import Annotated
import cloudinary
import cloudinary.uploader
import cloudinary.api

app = FastAPI(title="Advert Management API", version="1.0.0")




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
    # get all adverts from the database
    adverts = adverts_collection.find(
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
    return {"data": list(map(replace_mongo_id, Advert))}



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
    # insert the advert into the database
    adverts_collection.insert_one({
        "title": title,
        "description": description,
        "price": price,
        "category": category,
        "flyer_url": upload_result["secure_url"]
    })
    # adverts_collection.insert_one(event.model_dump())
    return {"message": "Advert added successfully"}


@app.get("/adverts/{advert_id}")
def get_advert_by_id(advert_id):
    # check if advert id is valid
    if not ObjectId.is_valid(advert_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid mongo id received") 
    # Get advert from database by id
    advert = adverts_collection.find_one({"_id": ObjectId(advert_id)})
    # Return response
    return {"data": replace_mongo_id(advert)}


@app.put("/adverts/{advert_id}")
def replace_advert(
    advert_id,
    title:Annotated[str,Form()],
    description:Annotated[str,Form()],
    flyer: Annotated[UploadFile,File()]):
    #check if advert_id is mongo_id
    if not ObjectId. is_valid(advert_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Invalid Mongo Id recieved")
    #upload flyer to cloudinary
    upload_result = cloudinary.uploader.upload(flyer,File)
    #replace advert in database
    adverts_collection.replace_one(
        filter={"_id":ObjectId (advert_id)},
        replacement={
        "title" : title,
        "description" : description,
        "flyer_url" : upload_result.get["secure_url"],
     }
    )
    #return response
    return {"message":"Hooray!Advert replaced successfully"}

@app.delete("/adverts/{adverts_id}")
def delete_advert(advert_id):
    #check if advert_id is Valid mongo db
    if not ObjectId. is_valid(advert_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "invalid Mongo ID received")
    #delete advert from database
    delete_results = adverts_collection.delete_one(filter= {"_id": ObjectId(advert_id)})
    #return response
    if not delete_results.deleted_count:
       raise HTTPException(status.HTTP_404_NOT_FOUND,"Oops no advert found to delete")
    return {"message":"Advert deleted successfully"}