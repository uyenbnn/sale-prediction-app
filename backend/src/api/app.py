from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config import MODEL_DIR
from src.api.routes.predict import router as predict_router

app = FastAPI(title="Sales Prediction API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(MODEL_DIR)), name="static")

app.include_router(predict_router, prefix="/api")
