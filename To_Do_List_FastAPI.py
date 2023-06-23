from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["todolist"]
todos_collection = db["todos"]

# Security
security = HTTPBasic()

class TodoCreate(BaseModel):
    title: str
    description: Optional[str]

class TodoUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]

# Helper functions
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user

def authenticate_user(username: str, password: str):
    # Dummy authentication logic, replace with your own implementation
    users = {"user1": "password1", "user2": "password2"}
    if users.get(username) == password:
        return username
    return None

# Routes
@app.post("/todos", status_code=201)
def create_todo(todo: TodoCreate, current_user: str = Depends(get_current_user)):
    new_todo = {"title": todo.title, "description": todo.description, "user": current_user}
    result = todos_collection.insert_one(new_todo)
    return {"id": str(result.inserted_id), "title": new_todo["title"], "description": new_todo["description"]}

@app.get("/todos/{todo_id}")
def read_todo(todo_id: str, current_user: str = Depends(get_current_user)):
    todo = todos_collection.find_one({"_id": ObjectId(todo_id), "user": current_user})
    todo['_id'] = str(todo['_id'])
    if not todo:
        raise HTTPException(status_code=404, detail= f"Todo not found {current_user}, {type(todo)=}")
    return todo

@app.get("/todos")
def read_todos(current_user: str = Depends(get_current_user)):
    print(current_user)
    todos = todos_collection.find({"user": current_user})
    todos_ = []
    for i in todos:
        i["_id"] = str(i["_id"])
        todos_.append(i)
    return {"TodoList" : todos_}

@app.put("/todos/{todo_id}")
def update_todo(todo_id: str, todo: TodoUpdate, current_user: str = Depends(get_current_user)):
    existing_todo = todos_collection.find_one({"_id": ObjectId(todo_id), "user": current_user})
    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    update_values = {k: v for k, v in todo.dict().items() if v is not None}
    todos_collection.update_one({"_id": ObjectId(todo_id)}, {"$set": update_values})
    return {"message": "Todo updated successfully"}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: str, current_user: str = Depends(get_current_user)):
    result = todos_collection.delete_one({"_id": ObjectId(todo_id), "user": current_user})
    # todo['_id'] = str(todo['_id'])
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}


#ToExecuteFollow
#uvicorn To_Do_List_FastAPI:app --reload
#http://127.0.0.1:8000/docs
