package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	_ "modernc.org/sqlite"

	"golang.org/x/crypto/bcrypt"
)

type Server struct {
	db *sql.DB
}

type createUserReq struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type userResp struct {
	ID        int64  `json:"id"`
	Email     string `json:"email"`
	CreatedAt int64  `json:"createdAt"`
}

type loginReq struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

func main() {
	port := getenv("PORT", "8080")
	dbPath := getenv("DB_PATH", "users.db")

	db, err := sql.Open("sqlite", dbPath)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Reasonable defaults
	db.SetMaxOpenConns(1) // SQLite often behaves best with low concurrency here

	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	if err := initSchema(ctx, db); err != nil {
		log.Fatal(err)
	}

	s := &Server{db: db}

	mux := http.NewServeMux()
	mux.HandleFunc("/users", s.handleUsers)      // POST /users, GET /users?email=...
	mux.HandleFunc("/users/", s.handleUserByID)  // GET /users/{id}
	mux.HandleFunc("/login", s.handleLogin)      // POST /login

	httpServer := &http.Server{
		Addr:              ":" + port,
		Handler:           logRequests(mux),
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       10 * time.Second,
		WriteTimeout:      10 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	log.Printf("DB: %s", dbPath)
	log.Printf("Listening on http://localhost:%s", port)
	log.Fatal(httpServer.ListenAndServe())
}

func initSchema(ctx context.Context, db *sql.DB) error {
	const schema = `
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
`
	_, err := db.ExecContext(ctx, schema)
	return err
}

func (s *Server) handleUsers(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodPost:
		s.createUser(w, r)
	case http.MethodGet:
		// GET /users?email=...
		email := strings.TrimSpace(r.URL.Query().Get("email"))
		if email == "" {
			writeJSON(w, http.StatusBadRequest, map[string]any{"error": "missing query param: email"})
			return
		}
		s.getUserByEmail(w, r, email)
	default:
		w.WriteHeader(http.StatusMethodNotAllowed)
	}
}

func (s *Server) handleUserByID(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}
	// Path: /users/{id}
	idStr := strings.TrimPrefix(r.URL.Path, "/users/")
	idStr = strings.Trim(idStr, "/")
	id, err := strconv.ParseInt(idStr, 10, 64)
	if err != nil || id <= 0 {
		writeJSON(w, http.StatusBadRequest, map[string]any{"error": "invalid user id"})
		return
	}
	s.getUserByID(w, r, id)
}

func (s *Server) createUser(w http.ResponseWriter, r *http.Request) {
	var req createUserReq
	if err := readJSON(r, &req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]any{"error": err.Error()})
		return
	}

	req.Email = strings.ToLower(strings.TrimSpace(req.Email))
	if req.Email == "" || !strings.Contains(req.Email, "@") {
		writeJSON(w, http.StatusBadRequest, map[string]any{"error": "invalid email"})
		return
	}
	if len(req.Password) < 8 {
		writeJSON(w, http.StatusBadRequest, map[string]any{"error": "password must be at least 8 characters"})
		return
	}

	hashBytes, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]any{"error": "failed to hash password"})
		return
	}

	now := time.Now().Unix()
	ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
	defer cancel()

	res, err := s.db.ExecContext(ctx,
		`INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)`,
		req.Email, string(hashBytes), now,
	)
	if err != nil {
		if isUniqueConstraintErr(err) {
			writeJSON(w, http.StatusConflict, map[string]any{"error": "email already exists"})
			return
		}
		writeJSON(w, http.StatusInternalServerError, map[string]any{"error": "db insert failed"})
		return
	}

	id, _ := res.LastInsertId()
	writeJSON(w, http.StatusCreated, userResp{
		ID:        id,
		Email:     req.Email,
		CreatedAt: now,
	})
}

func (s *Server) getUserByID(w http.ResponseWriter, r *http.Request, id int64) {
	ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
	defer cancel()

	var u userResp
	err := s.db.QueryRowContext(ctx,
		`SELECT id, email, created_at FROM users WHERE id = ?`,
		id,
	).Scan(&u.ID, &u.Email, &u.CreatedAt)

	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			writeJSON(w, http.StatusNotFound, map[string]any{"error": "user not found"})
			return
		}
		writeJSON(w, http.StatusInternalServerError, map[string]any{"error": "db query failed"})
		return
	}

	writeJSON(w, http.StatusOK, u)
}

func (s *Server) getUserByEmail(w http.ResponseWriter, r *http.Request, email string) {
	email = strings.ToLower(strings.TrimSpace(email))

	ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
	defer cancel()

	var u userResp
	err := s.db.QueryRowContext(ctx,
		`SELECT id, email, created_at FROM users WHERE email = ?`,
		email,
	).Scan(&u.ID, &u.Email, &u.CreatedAt)

	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			writeJSON(w, http.StatusNotFound, map[string]any{"error": "user not found"})
			return
		}
		writeJSON(w, http.StatusInternalServerError, map[string]any{"error": "db query failed"})
		return
	}

	writeJSON(w, http.StatusOK, u)
}

func (s *Server) handleLogin(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		w.WriteHeader(http.StatusMethodNotAllowed)
		return
	}

	var req loginReq
	if err := readJSON(r, &req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]any{"error": err.Error()})
		return
	}

	email := strings.ToLower(strings.TrimSpace(req.Email))
	if email == "" || req.Password == "" {
		writeJSON(w, http.StatusBadRequest, map[string]any{"error": "email and password required"})
		return
	}

	ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
	defer cancel()

	var id int64
	var passwordHash string
	var createdAt int64
	err := s.db.QueryRowContext(ctx,
		`SELECT id, password_hash, created_at FROM users WHERE email = ?`,
		email,
	).Scan(&id, &passwordHash, &createdAt)

	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			// Don’t reveal whether email exists
			writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "invalid credentials"})
			return
		}
		writeJSON(w, http.StatusInternalServerError, map[string]any{"error": "db query failed"})
		return
	}

	if bcrypt.CompareHashAndPassword([]byte(passwordHash), []byte(req.Password)) != nil {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "invalid credentials"})
		return
	}

	// Minimal “success” payload for the exercise
	writeJSON(w, http.StatusOK, map[string]any{
		"ok": true,
		"user": userResp{
			ID:        id,
			Email:     email,
			CreatedAt: createdAt,
		},
	})
}

func readJSON(r *http.Request, dst any) error {
	const maxBody = 1 << 20 // 1MB
	r.Body = http.MaxBytesReader(nil, r.Body, maxBody)
	defer r.Body.Close()

	dec := json.NewDecoder(r.Body)
	dec.DisallowUnknownFields()
	if err := dec.Decode(dst); err != nil {
		return fmt.Errorf("invalid json: %w", err)
	}
	// Ensure no trailing junk
	if dec.More() {
		return fmt.Errorf("invalid json: trailing data")
	}
	return nil
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

func isUniqueConstraintErr(err error) bool {
	// modernc.org/sqlite errors vary by wrapping; simplest reliable check for this exercise:
	msg := strings.ToLower(err.Error())
	return strings.Contains(msg, "unique constraint failed") ||
		strings.Contains(msg, "constraint failed") && strings.Contains(msg, "unique")
}

func logRequests(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		log.Printf("%s %s (%s)", r.Method, r.URL.Path, time.Since(start).Truncate(time.Millisecond))
	})
}

func getenv(k, def string) string {
	if v := strings.TrimSpace(os.Getenv(k)); v != "" {
		return v
	}
	return def
}
