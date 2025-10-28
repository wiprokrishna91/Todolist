# Simple Todo List App

A beautiful and simple todo list application built with FastAPI and PostgreSQL.

## Features

- 👥 User management (add new users)
- 📊 Personal dashboard for each user
- ✅ Add, complete, and delete todos
- 📱 Responsive design with colorful UI
- 🗄️ PostgreSQL database for data persistence

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run with Docker Compose:
```bash
docker-compose up -d
```

Or run locally (requires PostgreSQL):
```bash
python main.py
```

3. Open your browser and go to: `http://localhost:8000`

## Usage

1. **Home Page**: Welcome page with navigation
2. **Users Page**: Add new users and view existing ones
3. **Dashboard**: Personal todo dashboard for each user
   - View task statistics
   - Add new tasks
   - Mark tasks as complete/incomplete
   - Delete tasks

## API Endpoints

- `GET /` - Home page
- `GET /users` - Users management page
- `POST /users` - Create new user
- `GET /dashboard/{user_id}` - User dashboard
- `POST /todos` - Create new todo
- `POST /todos/{todo_id}/toggle` - Toggle todo completion
- `POST /todos/{todo_id}/delete` - Delete todo

## Database Schema

### Users Table
- id (SERIAL PRIMARY KEY)
- username (VARCHAR UNIQUE)
- email (VARCHAR UNIQUE)
- created_at (TIMESTAMP)

### Todos Table
- id (SERIAL PRIMARY KEY)
- user_id (INTEGER FOREIGN KEY)
- title (VARCHAR)
- description (TEXT)
- completed (BOOLEAN)
- created_at (TIMESTAMP)

## Docker Usage

Run the entire application with PostgreSQL:
```bash
docker-compose up -d
```

Stop the application:
```bash
docker-compose down
```