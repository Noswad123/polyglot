import os
import sqlite3
import time
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PORT = int(os.getenv("PORT", "8080"))
DB_PATH = os.getenv("DB_PATH", "users.db")

app = FastAPI(title="Users API (FastAPI + SQLite)")

# ---------- Models ----------

class CreateUserReq(BaseModel):
    email: EmailStr
    password: str

class UserResp(BaseModel):
    id: int
    email: EmailStr
    created_at: int

class LoginReq(BaseModel):
    email: EmailStr
    password: str


# ---------- DB helpers ----------

def ensure_db_dir(db_path: str) -> None:
    p = Path(db_path)
    if p.parent and str(p.parent) not in ("", "."):
        p.parent.mkdir(parents=True, exist_ok=True)

def get_conn() -> sqlite3.Connection:
    # Each request gets its own connection (simple + safe for this exercise)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_schema() -> None:
    ensure_db_dir(DB_PATH)
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              email TEXT NOT NULL UNIQUE,
              password_hash TEXT NOT NULL,
              created_at INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            """
        )

@app.on_event("startup")
def on_startup() -> None:
    init_schema()


# ---------- Routes ----------

@app.post("/users", response_model=UserResp, status_code=201)
def create_user(req: CreateUserReq) -> UserResp:
    email = req.email.strip().lower()

    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="password must be at least 8 characters")

    password_hash = pwd_context.hash(req.password)
    created_at = int(time.time())

    try:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
                (email, password_hash, created_at),
            )
            user_id = int(cur.lastrowid)
    except sqlite3.IntegrityError:
        # Unique constraint on email
        raise HTTPException(status_code=409, detail="email already exists")

    return UserResp(id=user_id, email=email, created_at=created_at)

@app.get("/users/{user_id}", response_model=UserResp)
def get_user_by_id(user_id: int) -> UserResp:
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="invalid user id")

    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="user not found")

    return UserResp(id=row["id"], email=row["email"], created_at=row["created_at"])

@app.get("/users", response_model=UserResp)
def get_user_by_email(email: str) -> UserResp:
    email_norm = email.strip().lower()
    if not email_norm:
        raise HTTPException(status_code=400, detail="missing query param: email")

    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, email, created_at FROM users WHERE email = ?",
            (email_norm,),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="user not found")

    return UserResp(id=row["id"], email=row["email"], created_at=row["created_at"])

@app.post("/login")
def login(req: LoginReq) -> Dict[str, Any]:
    email = req.email.strip().lower()

    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, email, password_hash, created_at FROM users WHERE email = ?",
            (email,),
        ).fetchone()

    # Don’t reveal whether the email exists
    if not row or not pwd_context.verify(req.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="invalid credentials")

    return {
        "ok": True,
        "user": {
            "id": row["id"],
            "email": row["email"],
            "created_at": row["created_at"],
        },
    }
