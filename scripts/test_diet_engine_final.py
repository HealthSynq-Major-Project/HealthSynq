"""
Final test runner for diet_engine_final.py.

Run from project root:
    $env:DATABASE_URL="paste_external_database_url_here"
    python scripts/test_diet_engine_final.py
"""

import os
from pathlib import Path
import sys
from urllib.parse import urlparse
import argparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass


def preflight_database_url():
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        print("DATABASE_URL is not set.")
        print("Set it first, or create E:\\project\\.env with DATABASE_URL=...")
        sys.exit(2)

    host = urlparse(database_url).hostname or ""
    if host.startswith("dpg-") and "." not in host:
        print("You are using Render's internal DB hostname.")
        print("Use Render's External Database URL for local testing.")
        sys.exit(2)


preflight_database_url()

import diet_engine_final as diet


def first_food(plan, slot, index=0):
    meal = plan[slot]
    if meal.empty or index >= len(meal):
        return ""
    return meal.iloc[index]["food_name"]


def print_case(title, plan):
    diet.display_plan(plan, title=title, show_scores=True)


def run_veg_skip_tests():
    # Use fixed seeds for repeatable testing. In production, pass seed=None.
    plan = diet.generate_daily_plan(
        glucose_mg_dl=130,
        daily_kcal=2200,
        diet="veg",
        seed=101,
        week_used={},
    )
    print_case("Original veg day", plan)

    breakfast_missed = first_food(plan, "breakfast", 0)
    print_case(
        f"After skipped breakfast item: {breakfast_missed}",
        diet.regenerate_day_after_feedback(
            original_plan=plan,
            actual_intake={"breakfast": {"__default__": 1.0}},
            not_eaten={"breakfast": [breakfast_missed]},
            completed_slots=["breakfast"],
            seed=200,
        ),
    )

    print_case(
        "After skipped full lunch",
        diet.regenerate_day_after_feedback(
            original_plan=plan,
            actual_intake={
                "breakfast": {"__default__": 1.0},
                "lunch": {"__default__": 0.0},
            },
            completed_slots=["breakfast", "lunch"],
            seed=201,
        ),
    )

    lunch_missed_1 = first_food(plan, "lunch", 0)
    print_case(
        f"After skipped lunch item: {lunch_missed_1}",
        diet.regenerate_day_after_feedback(
            original_plan=plan,
            actual_intake={
                "breakfast": {"__default__": 1.0},
                "lunch": {"__default__": 1.0},
            },
            not_eaten={"lunch": [lunch_missed_1]},
            completed_slots=["breakfast", "lunch"],
            seed=202,
        ),
    )

    lunch_missed_2 = [first_food(plan, "lunch", 0), first_food(plan, "lunch", 1)]
    lunch_missed_2 = [food for food in lunch_missed_2 if food]
    print_case(
        f"After skipped two lunch items: {', '.join(lunch_missed_2)}",
        diet.regenerate_day_after_feedback(
            original_plan=plan,
            actual_intake={
                "breakfast": {"__default__": 1.0},
                "lunch": {"__default__": 1.0},
            },
            not_eaten={"lunch": lunch_missed_2},
            completed_slots=["breakfast", "lunch"],
            seed=203,
        ),
    )

    snack_missed = first_food(plan, "snack", 0)
    print_case(
        f"After skipped snack item: {snack_missed}",
        diet.regenerate_day_after_feedback(
            original_plan=plan,
            actual_intake={
                "breakfast": {"__default__": 1.0},
                "lunch": {"__default__": 1.0},
                "snack": {"__default__": 1.0},
            },
            not_eaten={"snack": [snack_missed]},
            completed_slots=["breakfast", "lunch", "snack"],
            seed=204,
        ),
    )

    dinner_missed = [first_food(plan, "dinner", 0), first_food(plan, "dinner", 1)]
    dinner_missed = [food for food in dinner_missed if food]
    print_case(
        f"After skipped dinner items: {', '.join(dinner_missed)}",
        diet.regenerate_day_after_feedback(
            original_plan=plan,
            actual_intake={
                "breakfast": {"__default__": 1.0},
                "lunch": {"__default__": 1.0},
                "snack": {"__default__": 1.0},
                "dinner": {"__default__": 1.0},
            },
            not_eaten={"dinner": dinner_missed},
            completed_slots=["breakfast", "lunch", "snack", "dinner"],
            seed=205,
        ),
    )


def run_nonveg_high_glucose_tests():
    plan = diet.generate_daily_plan(
        glucose_mg_dl=160,
        daily_kcal=2400,
        diet="nonveg",
        seed=301,
        week_used={},
    )
    print_case("Original nonveg day | glucose 160 | 2400 kcal", plan)

    breakfast_missed = first_food(plan, "breakfast", 0)
    print_case(
        f"Nonveg after skipped breakfast item: {breakfast_missed}",
        diet.regenerate_day_after_feedback(
            original_plan=plan,
            actual_intake={"breakfast": {"__default__": 1.0}},
            not_eaten={"breakfast": [breakfast_missed]},
            completed_slots=["breakfast"],
            seed=302,
        ),
    )

    lunch_missed_2 = [first_food(plan, "lunch", 0), first_food(plan, "lunch", 1)]
    lunch_missed_2 = [food for food in lunch_missed_2 if food]
    print_case(
        f"Nonveg after skipped two lunch items: {', '.join(lunch_missed_2)}",
        diet.regenerate_day_after_feedback(
            original_plan=plan,
            actual_intake={
                "breakfast": {"__default__": 1.0},
                "lunch": {"__default__": 1.0},
            },
            not_eaten={"lunch": lunch_missed_2},
            completed_slots=["breakfast", "lunch"],
            seed=303,
        ),
    )

    snack_missed = first_food(plan, "snack", 0)
    print_case(
        f"Nonveg after skipped snack item: {snack_missed}",
        diet.regenerate_day_after_feedback(
            original_plan=plan,
            actual_intake={
                "breakfast": {"__default__": 1.0},
                "lunch": {"__default__": 1.0},
                "snack": {"__default__": 1.0},
            },
            not_eaten={"snack": [snack_missed]},
            completed_slots=["breakfast", "lunch", "snack"],
            seed=304,
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run final diet engine smoke tests.")
    parser.add_argument(
        "--case",
        choices=["all", "veg", "nonveg"],
        default="all",
        help="Choose which test set to print. Use --case nonveg for the glucose 160 / 2400 kcal test.",
    )
    args = parser.parse_args()

    if args.case in ("all", "veg"):
        run_veg_skip_tests()
    if args.case in ("all", "nonveg"):
        run_nonveg_high_glucose_tests()
