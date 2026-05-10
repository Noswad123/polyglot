use axum::{
    extract::{Path as AxumPath, Query, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use bcrypt::{hash, verify, DEFAULT_COST};
use serde::{Deserialize, Serialize};
use serde_json::json;
use sqlx::{Row, SqlitePool};
use std::{env, net::SocketAddr, time::SystemTime};
use tokio::{net::TcpListener, task};
use std::path::Path;
use sqlx::sqlite::SqliteConnectOptions;
use std::str::FromStr;

#[derive(Clone)]
struct AppState {
    pool: SqlitePool,
}

#[derive(Deserialize)]
struct CreateUserReq {
    email: String,
    password: String,
}

#[derive(Serialize)]
struct UserResp {
    id: i64,
    email: String,
    created_at: i64,
}

#[derive(Deserialize)]
struct LoginReq {
    email: String,
    password: String,
}

#[derive(Deserialize)]
struct EmailQuery {
    email: Option<String>,
}

#[derive(Debug)]
enum AppError {
    BadRequest(String),
    NotFound,
    Conflict(String),
    Internal(String),
}

impl IntoResponse for AppError {
    fn into_response(self) -> axum::response::Response {
        let (status, body) = match self {
            AppError::BadRequest(msg) => (StatusCode::BAD_REQUEST, json!({ "error": msg })),
            AppError::NotFound => (StatusCode::NOT_FOUND, json!({ "error": "not found" })),
            AppError::Conflict(msg) => (StatusCode::CONFLICT, json!({ "error": msg })),
            AppError::Internal(_) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                json!({ "error": "internal error" }),
            ),
        };
        (status, Json(body)).into_response()
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let port: u16 = env::var("PORT")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(8080);


    let db_path = env::var("DB_PATH").unwrap_or_else(|_| "users.db".to_string());

    // Ensure parent directory exists (SQLite will NOT create it)
    if let Some(parent) = Path::new(&db_path).parent() {
        if !parent.as_os_str().is_empty() {
            std::fs::create_dir_all(parent)?;
        }
    }

    // Now it is safe to build the SQLite URL
    let db_url = format!("sqlite://{}", db_path);
        // Build pool with options (this is where you tune max connections)
    let opts = SqliteConnectOptions::from_str(&db_url)?
        .create_if_missing(true);

    let pool = sqlx::sqlite::SqlitePoolOptions::new()
        .max_connections(5)
        .connect_with(opts)
        .await?;

    init_schema(&pool).await?;

    let state = AppState { pool };

    let app = Router::new()
        .route("/users", post(create_user).get(get_user_by_email_query))
        .route("/users/{id}", get(get_user_by_id))
        .route("/login", post(login))
        .with_state(state);

    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    println!("DB: {}", db_path);
    println!("Listening on http://{}", addr);

    let listener = TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

async fn init_schema(pool: &SqlitePool) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
"#,
    )
    .execute(pool)
    .await?;
    Ok(())
}

async fn create_user(
    State(state): State<AppState>,
    Json(payload): Json<CreateUserReq>,
) -> Result<impl IntoResponse, AppError> {
    let email = payload.email.trim().to_lowercase();
    if email.is_empty() || !email.contains('@') {
        return Err(AppError::BadRequest("invalid email".into()));
    }
    if payload.password.len() < 8 {
        return Err(AppError::BadRequest("password must be at least 8 characters".into()));
    }

    // Hash password off the async runtime thread
    let pw = payload.password;
    let password_hash = task::spawn_blocking(move || hash(pw, DEFAULT_COST))
        .await
        .map_err(|e| AppError::Internal(format!("join error: {e:?}")))?
        .map_err(|e| AppError::Internal(format!("hash error: {e}")))?;

    let now = SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .map_err(|e| AppError::Internal(format!("time error: {e}")))?
        .as_secs() as i64;

    let result = sqlx::query("INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)")
        .bind(&email)
        .bind(&password_hash)
        .bind(now)
        .execute(&state.pool)
        .await;

    match result {
        Ok(r) => {
            let id = r.last_insert_rowid();
            Ok((StatusCode::CREATED, Json(UserResp { id, email, created_at: now })))
        }
        Err(e) => {
            let msg = e.to_string().to_lowercase();
            if msg.contains("unique") || msg.contains("constraint") {
                Err(AppError::Conflict("email already exists".into()))
            } else {
                Err(AppError::Internal(format!("db error: {e}")))
            }
        }
    }
}

async fn get_user_by_id(
    State(state): State<AppState>,
    AxumPath(id): AxumPath<i64>,
) -> Result<impl IntoResponse, AppError> {
    if id <= 0 {
        return Err(AppError::BadRequest("invalid id".into()));
    }

    let row = sqlx::query("SELECT id, email, created_at FROM users WHERE id = ?")
        .bind(id)
        .fetch_optional(&state.pool)
        .await
        .map_err(|e| AppError::Internal(format!("db error: {e}")))?;

    match row {
        Some(r) => Ok((
            StatusCode::OK,
            Json(UserResp {
                id: r.get("id"),
                email: r.get("email"),
                created_at: r.get("created_at"),
            }),
        )),
        None => Err(AppError::NotFound),
    }
}

async fn get_user_by_email_query(
    State(state): State<AppState>,
    Query(q): Query<EmailQuery>,
) -> Result<impl IntoResponse, AppError> {
    let Some(email) = q.email else {
        return Err(AppError::BadRequest("missing query param: email".into()));
    };
    let email = email.trim().to_lowercase();
    if email.is_empty() {
        return Err(AppError::BadRequest("missing query param: email".into()));
    }

    let row = sqlx::query("SELECT id, email, created_at FROM users WHERE email = ?")
        .bind(&email)
        .fetch_optional(&state.pool)
        .await
        .map_err(|e| AppError::Internal(format!("db error: {e}")))?;

    match row {
        Some(r) => Ok((
            StatusCode::OK,
            Json(UserResp {
                id: r.get("id"),
                email: r.get("email"),
                created_at: r.get("created_at"),
            }),
        )),
        None => Err(AppError::NotFound),
    }
}

async fn login(
    State(state): State<AppState>,
    Json(payload): Json<LoginReq>,
) -> Result<impl IntoResponse, AppError> {
    let email = payload.email.trim().to_lowercase();
    let password = payload.password;

    if email.is_empty() || password.is_empty() {
        return Err(AppError::BadRequest("email and password required".into()));
    }

    let row = sqlx::query("SELECT id, password_hash, created_at FROM users WHERE email = ?")
        .bind(&email)
        .fetch_optional(&state.pool)
        .await
        .map_err(|e| AppError::Internal(format!("db error: {e}")))?;

    let Some(r) = row else {
        // keep it simple; you can use 401 if you prefer
        return Err(AppError::BadRequest("invalid credentials".into()));
    };

    let id: i64 = r.get("id");
    let password_hash: String = r.get("password_hash");
    let created_at: i64 = r.get("created_at");

    let verified = task::spawn_blocking(move || verify(password, &password_hash))
        .await
        .map_err(|e| AppError::Internal(format!("join error: {e:?}")))?
        .map_err(|e| AppError::Internal(format!("verify error: {e}")))?;

    if !verified {
        return Err(AppError::BadRequest("invalid credentials".into()));
    }

    Ok((
        StatusCode::OK,
        Json(json!({
            "ok": true,
            "user": { "id": id, "email": email, "created_at": created_at }
        })),
    ))
}
