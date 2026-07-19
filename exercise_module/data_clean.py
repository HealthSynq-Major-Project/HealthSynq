import json

with open("exercises.json", "r", encoding="utf-8") as f:
    data = json.load(f)

targets = {exercise["category"] for exercise in data if "category" in exercise}

for target in sorted(targets):

    print(target)