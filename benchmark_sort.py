import os
import json
import time
import copy
import heapq
from datetime import datetime


SORT_DIR = "sort"
SIZES = [100, 500, 1000, 2000]
ALGORITHMS = ["timsort", "bubble", "heap"]


def load_tasks(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["mylist"]["tasks"]


def get_sort_key(task, mode):
    deadline_time = datetime.strptime(
        task["deadline"],
        "%Y-%m-%d %H:%M"
    )

    if mode == "priority":
        return (
            task["completed"],
            -task["priority"],
            deadline_time
        )

    if mode == "deadline":
        return (
            task["completed"],
            deadline_time,
            -task["priority"]
        )


def timsort_tasks(tasks, mode):
    return sorted(
        tasks,
        key=lambda task: get_sort_key(task, mode)
    )


def bubble_sort_tasks(tasks, mode):
    tasks = tasks.copy()
    n = len(tasks)

    for i in range(n):
        swapped = False

        for j in range(0, n - i - 1):
            if get_sort_key(tasks[j], mode) > get_sort_key(tasks[j + 1], mode):
                tasks[j], tasks[j + 1] = tasks[j + 1], tasks[j]
                swapped = True

        if not swapped:
            break

    return tasks


def heap_sort_tasks(tasks, mode):
    heap = []

    for index, task in enumerate(tasks):
        heapq.heappush(
            heap,
            (
                get_sort_key(task, mode),
                index,
                task
            )
        )

    sorted_tasks = []

    while heap:
        sorted_tasks.append(
            heapq.heappop(heap)[2]
        )

    return sorted_tasks


def sort_tasks(tasks, mode, algorithm):
    if algorithm == "bubble":
        return bubble_sort_tasks(tasks, mode)

    if algorithm == "heap":
        return heap_sort_tasks(tasks, mode)

    return timsort_tasks(tasks, mode)


def measure_time(tasks, algorithm):

    # =====================
    # Warmup
    # =====================

    warmup_copy = copy.deepcopy(tasks)

    sort_tasks(
        warmup_copy,
        mode="deadline",
        algorithm=algorithm
    )

    # =====================
    # 正式計時
    # =====================

    tasks_copy = copy.deepcopy(tasks)

    start = time.perf_counter()

    sort_tasks(
        tasks_copy,
        mode="deadline",
        algorithm=algorithm
    )

    end = time.perf_counter()

    return end - start


def benchmark():

    print()
    print("Priority → Deadline 排序效率測試")
    print()

    print(
        f"{'資料量':<10}"
        f"{'Timsort':<15}"
        f"{'Bubble':<15}"
        f"{'Heap':<15}"
    )

    print("-" * 55)

    for size in SIZES:

        path = os.path.join(
            SORT_DIR,
            f"tasks_{size}.json"
        )

        tasks = load_tasks(path)

        results = {}

        for algorithm in ALGORITHMS:

            results[algorithm] = measure_time(
                tasks,
                algorithm
            )

        print(
            f"{size:<10}"
            f"{results['timsort']:<15.8f}"
            f"{results['bubble']:<15.8f}"
            f"{results['heap']:<15.8f}"
        )


benchmark()