from datetime import datetime, timezone
import random

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
import pandas as pd

from diet_engine_final import (
    generate_daily_plan,
    generate_dynamic_meal,
    generate_dynamic_plan,
    regenerate_day_after_feedback,
)
from exercise_module.main import generate_workout
app = FastAPI()

class DietRequest(BaseModel):
    glucose_mg_dl: float
    daily_kcal: int
    diet: str
    week_used: dict[str, list[list[str]]] = Field(default_factory=dict)

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

class DietFeedbackRequest(BaseModel):
    original_plan: dict
    actual_intake: dict[str, dict[str, float]] = Field(default_factory=dict)
    not_eaten: dict[str, list[str]] = Field(default_factory=dict)
    completed_slots: list[str] = Field(default_factory=list)
    burned_kcal_so_far: float = 0.0
    burn_compensation_ratio: float | None = None
    max_extra_kcal_ratio: float = 0.35
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

def plan_to_json(plan):
    payload = {
        "summary": plan["summary"],
        "breakfast": df_to_records(plan["breakfast"]),
        "lunch": df_to_records(plan["lunch"]),
        "snack": df_to_records(plan["snack"]),
        "dinner": df_to_records(plan["dinner"]),
        "week_used": week_used_to_json(plan.get("week_used", {})),
    }
    if "confirmed_week_used" in plan:
        payload["confirmed_week_used"] = week_used_to_json(plan.get("confirmed_week_used", {}))
    return jsonable_encoder(payload)

def meal_records_to_df(records):
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)

def request_plan_to_engine_plan(raw_plan):
    return {
        "summary": raw_plan.get("summary", {}),
        "breakfast": meal_records_to_df(raw_plan.get("breakfast", [])),
        "lunch": meal_records_to_df(raw_plan.get("lunch", [])),
        "snack": meal_records_to_df(raw_plan.get("snack", [])),
        "dinner": meal_records_to_df(raw_plan.get("dinner", [])),
    }

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
        diet=req.diet,
        week_used=normalize_week_used(req.week_used),
    )

    return plan_to_json(plan)

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

    return plan_to_json(plan)

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

@app.post("/regenerate-diet-after-feedback")
def regenerate_diet_after_feedback(req: DietFeedbackRequest):
    ratio = req.burn_compensation_ratio if req.burn_compensation_ratio is not None else 0.50

    plan = regenerate_day_after_feedback(
        original_plan=request_plan_to_engine_plan(req.original_plan),
        actual_intake=req.actual_intake,
        not_eaten=req.not_eaten,
        completed_slots=req.completed_slots,
        burned_kcal_so_far=req.burned_kcal_so_far,
        burn_compensation_ratio=ratio,
        max_extra_kcal_ratio=req.max_extra_kcal_ratio,
        previous_week_used=normalize_week_used(req.week_used),
    )

    return plan_to_json(plan)
