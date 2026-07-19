import random

COMMON = [
    "body weight",
    "dumbbell",
    "barbell",
    "cable",
    "band"
]


def filter_category(exercises, category):
    filtered = []

    for exercise in exercises:
        if exercise["category"].lower() == category.lower():
            filtered.append(exercise)

    return filtered


def common_workout(equipment_groups):

    # Shuffle each equipment group
    for exercises in equipment_groups.values():
        random.shuffle(exercises)

    workout = []

    while len(workout) < 10:

        added = False

        for equipment in COMMON:

            if equipment in equipment_groups and len(equipment_groups[equipment]) > 0:

                workout.append(equipment_groups[equipment].pop(0))
                added = True

                if len(workout) == 10:
                    break

        if not added:
            break

    return workout


def special_workout(equipment_groups):

    special = []

    for equipment, exercises in equipment_groups.items():

        if equipment not in COMMON:
            special.extend(exercises)

    random.shuffle(special)

    return special[:2]