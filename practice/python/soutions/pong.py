from fastapi import FastAPI, Response

# uvicorn pong:app --host 127.0.0.1 --port 8080
# # or pick a port:
# uvicorn pong:app --host 127.0.0.1 --port ${PORT:-8080}

app = FastAPI()


@app.get("/ping")
def ping():
    return Response(content="pong", media_type="text/plain")
