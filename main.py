from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from aiofiles import open
import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model
import numpy as np
import utils, authentication, models, schemas, database
from sqlalchemy.orm import Session
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi.security import OAuth2PasswordRequestForm



app = FastAPI(title="Cifar10 with keras Model",
    description="Laboratory  exposing predictive model using FastAPI",
    version="1.0.0",
)

class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
model = load_model('D:\\fastApi_lab\\upload_photos\\cifar10.h5')

database.Base.metadata.create_all(database.engine)#roda magration com as definições do model

@app.post("/uploadfile/", tags=["model"])
async def create_upload_file(new_file: UploadFile = File(...),user=Depends(authentication.manager)):
    file_name = os.getcwd() + "/images/" + new_file.filename
    up_file = await new_file.read()
    
    if new_file.content_type not in ['image/jpeg', 'image/png']:
        raise HTTPException(status_code=406, detail="Please upload only .jpeg and .png files")
    async with open(f"{file_name}", "wb") as f:
        await f.write(up_file)
    img =utils.preprocess_image(file_name)
    predict =model.predict(img)
    new_pred=models.Prediction(class_id=int(np.argmax(predict)),class_name=class_names[np.argmax(predict)])
    return new_pred 

@app.post('/user', response_model=schemas.ShowUser, tags=["user manager"])
def create_user(request: schemas.User,db: Session = Depends(database.get_db),user=Depends(authentication.manager)):
    
    if user.role != authentication.roles[0]:
        raise HTTPException(status_code=401)
    verify_user = db.query(models.User).filter(models.User.email==request.email).first()
    if not verify_user:
        hashedPassword = utils.pwd_cxt.hash(request.password)
        new_user= models.User(name=request.name,email=request.email,password=hashedPassword,role=request.role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    else:
        raise HTTPException(status_code=409, detail="user already exist")
    return new_user

@app.get('/adm_base', tags=["user manager"])
def create_default_adm(db: Session = Depends(database.get_db)):
    response = 'Already Created'
    email = 'admin@system.com'
    adm = db.query(models.User).filter(models.User.email==email).first()
    if not adm:
        hashedPassword = utils.pwd_cxt.hash('pass')
        new_user= models.User(name='admin',email=email,password=hashedPassword,role=authentication.roles[0])
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        response = 'Created'
    return response

@app.post('/auth', tags=["user manager"])
def login(request: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(database.get_db)):
   
    @authentication.manager.user_loader
    def get_user(email):
        user = db.query(models.User).filter(models.User.email==email).first()
        return user

    user =get_user(request.username)
    
    if  not user:
        raise InvalidCredentialsException
    if not utils.verify_pass(user.password,request.password):
        raise InvalidCredentialsException
    access_token = authentication.manager.create_access_token(data=dict(sub=user.email))

    return {'access_token': access_token, 'token_type': 'bearer'}