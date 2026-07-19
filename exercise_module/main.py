import json
from collections import defaultdict

from .helpers import (
    filter_category,
    common_workout,
    special_workout
)

with open("exercise_module/clean_exercises.json", "r", encoding="utf-8") as file:
    exercises = json.load(file)


def generate_workout(category):

    filtered_exercises = filter_category(exercises, category)

    if not filtered_exercises:
        return {
            "success": False,
            "message": f"No exercises found for category '{category}'"
        }

    equipment_groups = defaultdict(list)

    for exercise in filtered_exercises:
        equipment_groups[exercise["equipment"]].append(exercise)

    workout = common_workout(equipment_groups)
    workout.extend(special_workout(equipment_groups))

    return {
        "success": True,
        "category": category,
        "count": len(workout),
        "workout": workout
    }


if __name__ == "__main__":

    category = input("Enter category: ").strip()

    result = generate_workout(category)

    print(json.dumps(result, indent=4, ensure_ascii=False))