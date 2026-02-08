A database will be created for users if it doesn't already exist


create user
```bash
curl -s -X POST http://localhost:8080/users \
  -H 'content-type: application/json' \
  -d '{"email":"a@example.com","password":"password123"}' | jq
```


fetch by id
```bash
curl -s http://localhost:8080/users/1 | jq
```

Fetch by email
```bash
curl -s "http://localhost:8080/users?email=a@example.com" | jq
 ```

Login
```bash
curl -s -X POST http://localhost:8080/login \
  -H 'content-type: application/json' \
  -d '{"email":"a@example.com","password":"password123"}' | jq
```

