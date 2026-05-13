from .database import Base, engine
from . import models

from fastapi import FastAPI

from .routers import posts, users, communities, debug

app = FastAPI(title="Circlo Backend")

# Attach routers
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(communities.router)
app.include_router(debug.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Circlo Backend is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
