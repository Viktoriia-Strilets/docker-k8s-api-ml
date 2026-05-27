from datetime import datetime
import time
from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import models, database


time.sleep(5)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# --- ГОЛОВНА СТОРІНКА ---
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(database.get_db)):
    # Сортуємо: спочатку невиконані, потім виконані
    todos = db.query(models.Todo).order_by(models.Todo.completed, models.Todo.id.desc()).all()
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"todo_list": todos}
    )

# --- ДОДАТИ ЗАВДАННЯ ---
@app.post("/add")
def add(title: str = Form(...), db: Session = Depends(database.get_db)):
    new_todo = models.Todo(title=title)
    db.add(new_todo)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# --- ОНОВИТИ СТАТУС (ВИКОНАНО/НЕ ВИКОНАНО) ---
@app.get("/update/{todo_id}")
def update(todo_id: int, db: Session = Depends(database.get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo:
        todo.completed = not todo.completed  # Перемикаємо статус
        db.commit()
    return RedirectResponse(url="/")

# --- ВИДАЛИТИ ЗАВДАННЯ ---
@app.get("/delete/{todo_id}")
def delete(todo_id: int, db: Session = Depends(database.get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo:
        db.delete(todo)
        db.commit()
    return RedirectResponse(url="/")

# --- REST API ---
@app.get("/api/todos")
def get_todos_api(db: Session = Depends(database.get_db)):
    return db.query(models.Todo).all()

@app.get("/write-log")
def write_log():
    with open("/logs/app.log", "a") as f:
        f.write(f"Log entry at {datetime.now()}\n")
    return {"status": "logged"}