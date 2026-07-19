from datetime import datetime, timezone
import random

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
import pandas as pd

from diet_engine import generate_daily_plan, generate_dynamic_meal, generate_dynamic_plan
from exercise_module.main import generate_workout
app = FastAPI()

class DietRequest(BaseModel):
    glucose_mg_dl: float
    daily_kcal: int
    diet: str

class DynamicDietRequest(BaseModel):
    glucose_mg_dl: float
    daily_kcal: int
    diet: str
    current_slot: str
    consumed_kcal_so_far: float = 0.0
    burned_kcal_so_far: float = 0.0
    burn_compensation_ratio: float | None = None
    max_extra_kcal_ratio: float = 0.50
    already_used_foods: list[str] = Field(default_factory=list)
    week_used: dict[str, list[list[str]]] = Field(default_factory=dict)

class DynamicMealRequest(BaseModel):
    glucose_mg_dl: float
    daily_kcal: int
    diet: str
    meal_slot: str
    consumed_kcal_so_far: float = 0.0
    burned_kcal_so_far: float = 0.0
    burn_compensation_ratio: float | None = None
    max_extra_kcal_ratio: float = 0.50
    already_used_foods: list[str] = Field(default_factory=list)
    week_used: dict[str, list[list[str]]] = Field(default_factory=dict)

class WorkoutRequest(BaseModel):
    category: str

@app.post("/generate-workout")
def generate_workout_api(request: WorkoutRequest):

    if not request.category:
        raise HTTPException(
            status_code=400,
            detail="Category is required"
        )

    return generate_workout(request.category)

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

def normalize_week_used(raw):
    out = {}
    for role, items in (raw or {}).items():
        safe_items = []
        if not isinstance(items, list):
            continue
        for pair in items:
            if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                safe_items.append((str(pair[0]), str(pair[1])))
        out[str(role)] = safe_items
    return out

def week_used_to_json(week_used):
    return {role: [[a, b] for (a, b) in items] for role, items in (week_used or {}).items()}

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

@app.post("/generate-diet-dynamic")
def generate_diet_dynamic(req: DynamicDietRequest):
    ratio = req.burn_compensation_ratio if req.burn_compensation_ratio is not None else 0.65

    plan = generate_dynamic_plan(
        glucose_mg_dl=req.glucose_mg_dl,
        daily_kcal=req.daily_kcal,
        diet=req.diet,
        current_slot=req.current_slot,
        consumed_kcal_so_far=req.consumed_kcal_so_far,
        burned_kcal_so_far=req.burned_kcal_so_far,
        burn_compensation_ratio=ratio,
        max_extra_kcal_ratio=req.max_extra_kcal_ratio,
        already_used_foods=req.already_used_foods,
        week_used=normalize_week_used(req.week_used),
    )

    return jsonable_encoder({
        "summary": plan["summary"],
        "breakfast": df_to_records(plan["breakfast"]),
        "lunch": df_to_records(plan["lunch"]),
        "dinner": df_to_records(plan["dinner"]),
        "snack": df_to_records(plan["snack"]),
        "week_used": week_used_to_json(plan["week_used"]),
    })

@app.post("/generate-meal-dynamic")
def generate_meal_dynamic(req: DynamicMealRequest):
    ratio = req.burn_compensation_ratio if req.burn_compensation_ratio is not None else 0.65

    plan = generate_dynamic_meal(
        glucose_mg_dl=req.glucose_mg_dl,
        daily_kcal=req.daily_kcal,
        diet=req.diet,
        meal_slot=req.meal_slot,
        consumed_kcal_so_far=req.consumed_kcal_so_far,
        burned_kcal_so_far=req.burned_kcal_so_far,
        burn_compensation_ratio=ratio,
        max_extra_kcal_ratio=req.max_extra_kcal_ratio,
        already_used_foods=req.already_used_foods,
        week_used=normalize_week_used(req.week_used),
    )

    return jsonable_encoder({
        "summary": plan["summary"],
        "meal": df_to_records(plan["meal"]),
        "week_used": week_used_to_json(plan["week_used"]),
    })
