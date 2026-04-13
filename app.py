from datetime import datetime, timezone
import random

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import pandas as pd

from diet_engine import generate_daily_plan

app = FastAPI()

class DietRequest(BaseModel):
    glucose_mg_dl: float
    daily_kcal: int
    diet: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.api_route("/ping", methods=["GET", "HEAD"])
def ping():
    return {
        "status": "ok",
        "message": random.choice(["ok", "yumbedded"]),
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }

def df_to_records(df):
    if df is None or df.empty:
        return []
    df = df.where(pd.notnull(df), None)
    return jsonable_encoder(df.to_dict(orient="records"))

@app.post("/generate-diet")
def generate_diet(req: DietRequest):
    plan = generate_daily_plan(
        glucose_mg_dl=req.glucose_mg_dl,
        daily_kcal=req.daily_kcal,
        diet=req.diet
    )

    return jsonable_encoder({
        "summary": plan["summary"],
        "breakfast": df_to_records(plan["breakfast"]),
        "lunch": df_to_records(plan["lunch"]),
        "dinner": df_to_records(plan["dinner"]),
        "snack": df_to_records(plan["snack"]),
    })
