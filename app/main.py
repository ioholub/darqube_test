from fastapi import FastAPI
from darqube_test.app.routes import router as user_router


app = FastAPI()
app.include_router(user_router, tags=["user"], prefix="")


@app.get("/api")
def root():
    return {"message": "Hello Word"}


