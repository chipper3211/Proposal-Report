import os
import json
import random
import uuid
from datetime import datetime, timedelta


SORT_DIR = "sort"
SIZES = [100, 500, 1000, 2000]


def generate_task(index):
    base_time = datetime(2026, 5, 10, 18, 0)
    random_minutes = random.randint(0, 100000)

    return {
        "id": str(uuid.uuid4()),
        "name": f"任務{index}",
        "deadline": (
            base_time + timedelta(minutes=random_minutes)
        ).strftime("%Y-%m-%d %H:%M"),
        "priority": random.randint(1, 5),
        "completed": random.choice([True, False])
    }


def priority_sort_key(task):
    deadline_time = datetime.strptime(
        task["deadline"],
        "%Y-%m-%d %H:%M"
    )

    return (
        task["completed"],
        -task["priority"],
        deadline_time
    )


def save_json(path, tasks):
    data = {
        "mylist": {
            "reward": "測試獎勵",
            "tasks": tasks
        }
    }

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def main():
    os.makedirs(SORT_DIR, exist_ok=True)

    for size in SIZES:
        tasks = [
            generate_task(i)
            for i in range(size)
        ]

        sorted_tasks = sorted(
            tasks,
            key=priority_sort_key
        )

        path = os.path.join(
            SORT_DIR,
            f"tasks_{size}.json"
        )

        save_json(path, sorted_tasks)

        print(f"已產生 priority 優先排序資料：{path}")


main()