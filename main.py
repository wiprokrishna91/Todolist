from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import mysql.connector
from datetime import datetime
from typing import List, Optional
import uvicorn
import os
import csv

app = FastAPI(title="Simple Todo App")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'todoapp'),
    'user': os.getenv('DB_USER', 'mysql'),
    'password': os.getenv('DB_PASSWORD', 'mysql'),
    'port': os.getenv('DB_PORT', '3306')
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Todos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Load users from CSV
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        with open('users.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", 
                              (row['name'], row['email']))
                if row['name'] == 'admin':
                    admin_id = cursor.lastrowid
                    cursor.execute("INSERT INTO todos (user_id, title, description) VALUES (%s, %s, %s)", 
                                  (admin_id, "Cleanup the code", "Refactor and optimize the codebase"))
                    cursor.execute("INSERT INTO todos (user_id, title, description) VALUES (%s, %s, %s)", 
                                  (admin_id, "Create new tasks for users", "Add functionality for users to create tasks"))
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/users", response_class=HTMLResponse)
async def users_page(request: Request):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

@app.post("/users")
async def create_user(username: str = Form(...), email: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (username, email))
        conn.commit()
    except mysql.connector.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    conn.close()
    return RedirectResponse(url="/users", status_code=303)

@app.get("/dashboard/{user_id}", response_class=HTMLResponse)
async def user_dashboard(request: Request, user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user info
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's todos
    cursor.execute("SELECT * FROM todos WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    todos = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": user, 
        "todos": todos
    })

@app.post("/todos")
async def create_todo(
    user_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(default="")
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (user_id, title, description) VALUES (%s, %s, %s)",
        (user_id, title, description)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/dashboard/{user_id}", status_code=303)

@app.post("/todos/{todo_id}/toggle")
async def toggle_todo(todo_id: int, user_id: int = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE todos SET completed = NOT completed WHERE id = %s", (todo_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/dashboard/{user_id}", status_code=303)

@app.post("/todos/{todo_id}/delete")
async def delete_todo(todo_id: int, user_id: int = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url=f"/dashboard/{user_id}", status_code=303)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)