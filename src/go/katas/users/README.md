# Setup
go mod init pong-users
go get modernc.org/sqlite
go get golang.org/x/crypto/bcrypt
go run main.go
-- or: --
DB_PATH=users.db PORT=8080 go run main.go



