from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pymongo import MongoClient
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()
env = os.environ

client = MongoClient(env["CONNECTION_STRING"])
db = client[env["DB"]]
collection = db[env["COLLECTION"]]

templates = Jinja2Templates(directory="./")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Register(BaseModel):
    name:str
    age:int
    username:str
    password:str

class Hasher():
    def __init__(self,password):
        self.password = password
    def get_password_hash(self):
        return pwd_context.hash(self.password)
    def verify_password(self, hashed_password):
        return pwd_context.verify(self.password, hashed_password)

@app.get("/", response_class=HTMLResponse)
async def home(request:Request):
    return templates.TemplateResponse("index.html", {"request":request})

@app.get("/register-form", response_class=HTMLResponse)
async def register_form(request:Request):
    return templates.TemplateResponse("register.html", {"request":request})

@app.post("/register")
async def register(name:str=Form(...), age:int=Form(...), username:str=Form(...), password:str=Form(...)):
    check_data = collection.find_one({"username":username})
    if(check_data):
        return "มีชื่อผู้ใช้ (Username) นี้อยู่เเล้ว"
    Password = Hasher(password)
    data = {"name":name, "age":age, "username":username, "password":Password.get_password_hash()}
    register = Register(**data)
    collection.insert_one(register.dict())
    return "ลงทะเบียนสำเร็จ !!!"

@app.get("/login-form", response_class=HTMLResponse)
async def login_form(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

@app.post("/login", response_class=HTMLResponse)
async def login(username:str=Form(...), password:str=Form(...), **request:Request):
    data = collection.find_one({"username": username})
    if(data):
        Password = Hasher(password)
        if(Password.verify_password(data["password"])):
            return data["name"]
        return "รหัสผ่านไม่ถูกต้อง"
    return "ไม่มีชื่อผู้ใช้ (Username) นี้"









