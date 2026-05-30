import os
import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import uuid
import heapq
import random
import copy
import time

# =========================
# 路徑設定
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.join(BASE_DIR, "data.json")

# =========================
# 資料處理
# =========================

def load_data():
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return {}


def save_data(data):
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# =========================
# 排序
# =========================
def get_sort_key(task, mode="priority"):

    deadline_time = datetime.strptime(
        task["deadline"],
        "%Y-%m-%d %H:%M"
    )

    if mode == "deadline":
        return (
            task["completed"],
            deadline_time,
            -task["priority"]
        )

    return (
        task["completed"],
        -task["priority"],
        deadline_time
    )

def timsort_tasks(tasks, mode="priority"):

    return sorted(
        tasks,
        key=lambda task: get_sort_key(task, mode)
    )


def bubble_sort_tasks(tasks, mode="priority"):

    tasks = tasks.copy()
    n = len(tasks)

    for i in range(n):

        for j in range(0, n - i - 1):

            if get_sort_key(tasks[j], mode) > get_sort_key(tasks[j + 1], mode):

                tasks[j], tasks[j + 1] = tasks[j + 1], tasks[j]

    return tasks


def heap_sort_tasks(tasks, mode="priority"):

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


def sort_tasks(tasks, mode="priority", algorithm="timsort"):

    if algorithm == "bubble":
        return bubble_sort_tasks(tasks, mode)

    elif algorithm == "heap":
        return heap_sort_tasks(tasks, mode)

    else:
        return timsort_tasks(tasks, mode)
# =========================
# Todo Lists
# =========================

def refresh_lists():

    listbox_lists.delete(0, tk.END)

    data = load_data()

    for name in data.keys():
        listbox_lists.insert(tk.END, name)


def add_todo_list():

    name = entry_list_name.get().strip()

    if not name:
        return

    data = load_data()

    if name in data:
        messagebox.showwarning("警告", "清單已存在")
        return

    data[name] = {
        "reward": "",
        "tasks": []
    }

    save_data(data)

    refresh_lists()

    entry_list_name.delete(0, tk.END)

def delete_todo_list():

    selected = listbox_lists.curselection()

    if not selected:
        messagebox.showwarning("警告", "請先選擇要刪除的清單")
        return

    list_name = listbox_lists.get(selected)

    confirm = messagebox.askyesno(
        "確認刪除",
        f"確定要刪除清單「{list_name}」嗎？\n\n清單內的所有任務也會一起刪除。"
    )

    if not confirm:
        return

    data = load_data()

    if list_name in data:
        del data[list_name]

    save_data(data)

    refresh_lists()

    for item in tree.get_children():
        tree.delete(item)

# =========================
# 顯示任務
# =========================

def show_tasks(event=None):

    for item in tree.get_children():
        tree.delete(item)

    selected = listbox_lists.curselection()

    if not selected:
        return

    list_name = listbox_lists.get(selected)

    data = load_data()

    sort_mode = sort_mode_var.get()

    sort_mode = sort_mode_var.get()
    sort_algorithm = sort_algorithm_var.get()

    tasks = sort_tasks(
        data[list_name]["tasks"],
        mode=sort_mode,
        algorithm=sort_algorithm
    )

    for task in tasks:

        status = "✓" if task["completed"] else "✗"

        if task["completed"]:
            tag = "completed"

        elif task["priority"] >= 5:
            tag = "high"

        elif task["priority"] >= 3:
            tag = "medium"

        else:
            tag = "low"

        tree.insert(
            "",
            tk.END,
            iid=task["id"],
            values=(
                status,
                task["name"],
                task["deadline"],
                task["priority"]
            ),
            tags=(tag,)
        )


# =========================
# 新增任務
# =========================

def add_task():

    selected = listbox_lists.curselection()

    if not selected:
        messagebox.showwarning("警告", "請先選擇清單")
        return

    name = entry_task_name.get().strip()
    deadline = entry_deadline.get().strip()

    if not name:
        messagebox.showwarning("警告", "請輸入任務名稱")
        return

    try:
        priority = int(entry_priority.get())

    except:
        messagebox.showwarning("警告", "優先級必須是數字")
        return

    try:
        datetime.strptime(deadline, "%Y-%m-%d %H:%M")

    except:
        messagebox.showwarning(
            "警告",
            "時間格式錯誤\n格式: YYYY-MM-DD HH:MM"
        )
        return

    task = {
        "id": str(uuid.uuid4()),
        "name": name,
        "deadline": deadline,
        "priority": priority,
        "completed": False
    }

    list_name = listbox_lists.get(selected)

    data = load_data()

    data[list_name]["tasks"].append(task)

    save_data(data)

    show_tasks()

    entry_task_name.delete(0, tk.END)


# =========================
# 取得選中任務
# =========================

def get_selected_task():

    selected_list = listbox_lists.curselection()

    if not selected_list:
        return None, None

    selected_item = tree.selection()

    if not selected_item:
        return None, None

    list_name = listbox_lists.get(selected_list)

    task_id = selected_item[0]

    return list_name, task_id


# =========================
# 標記完成
# =========================

def complete_task():

    result = get_selected_task()

    if result == (None, None):
        return

    list_name, task_id = result

    data = load_data()

    for task in data[list_name]["tasks"]:

        if task["id"] == task_id:
            task["completed"] = True
            break

    save_data(data)

    # 檢查是否全部完成
    unfinished = [

        t for t in data[list_name]["tasks"]

        if not t["completed"]
    ]

    if len(unfinished) == 0:

        reward = data[list_name]["reward"]

        if reward.strip():

            messagebox.showinfo(
                "🎉 恭喜完成所有任務！",
                f"你的獎勵：\n\n{reward}"
            )

    show_tasks()


# =========================
# 刪除任務
# =========================

def delete_task():

    result = get_selected_task()

    if result == (None, None):
        return

    list_name, task_id = result

    data = load_data()

    data[list_name]["tasks"] = [

        task for task in data[list_name]["tasks"]

        if task["id"] != task_id
    ]

    save_data(data)

    show_tasks()


# =========================
# 雙擊編輯
# =========================

def edit_task(event):

    result = get_selected_task()

    if result == (None, None):
        return

    list_name, task_id = result

    data = load_data()

    selected_task = None

    for task in data[list_name]["tasks"]:

        if task["id"] == task_id:
            selected_task = task
            break

    if not selected_task:
        return

    # 編輯視窗

    edit_window = tk.Toplevel(root)

    edit_window.title("編輯任務")
    edit_window.geometry("400x300")
    edit_window.configure(bg="#2b2b2b")

    tk.Label(
        edit_window,
        text="任務名稱",
        bg="#2b2b2b",
        fg="white"
    ).pack(pady=5)

    name_entry = tk.Entry(
        edit_window,
        width=30,
        bg="#333",
        fg="white",
        insertbackground="white"
    )

    name_entry.pack()

    name_entry.insert(0, selected_task["name"])

    tk.Label(
        edit_window,
        text="截止時間",
        bg="#2b2b2b",
        fg="white"
    ).pack(pady=5)

    deadline_entry = tk.Entry(
        edit_window,
        width=30,
        bg="#333",
        fg="white",
        insertbackground="white"
    )

    deadline_entry.pack()

    deadline_entry.insert(0, selected_task["deadline"])

    tk.Label(
        edit_window,
        text="優先級",
        bg="#2b2b2b",
        fg="white"
    ).pack(pady=5)

    priority_entry = tk.Entry(
        edit_window,
        width=30,
        bg="#333",
        fg="white",
        insertbackground="white"
    )

    priority_entry.pack()

    priority_entry.insert(0, selected_task["priority"])

    def save_edit():

        try:
            priority = int(priority_entry.get())

            datetime.strptime(
                deadline_entry.get(),
                "%Y-%m-%d %H:%M"
            )

        except:
            messagebox.showwarning(
                "警告",
                "輸入格式錯誤"
            )
            return

        selected_task["name"] = name_entry.get()
        selected_task["deadline"] = deadline_entry.get()
        selected_task["priority"] = priority

        save_data(data)

        show_tasks()

        edit_window.destroy()

    tk.Button(
        edit_window,
        text="儲存修改",
        command=save_edit,
        bg="#444",
        fg="white"
    ).pack(pady=20)


# =========================
# 設定獎勵
# =========================

def set_reward():

    selected = listbox_lists.curselection()

    if not selected:
        messagebox.showwarning("警告", "請先選擇清單")
        return

    list_name = listbox_lists.get(selected)

    data = load_data()

    reward_window = tk.Toplevel(root)

    reward_window.title("設定獎勵")
    reward_window.geometry("400x200")
    reward_window.configure(bg="#2b2b2b")

    tk.Label(
        reward_window,
        text="完成所有任務後的獎勵",
        bg="#2b2b2b",
        fg="white",
        font=("Arial", 12)
    ).pack(pady=10)

    reward_entry = tk.Entry(
        reward_window,
        width=35,
        bg="#333",
        fg="white",
        insertbackground="white"
    )

    reward_entry.pack(pady=10)

    current_reward = data[list_name]["reward"]

    reward_entry.insert(0, current_reward)

    def save_reward():

        data[list_name]["reward"] = reward_entry.get()

        save_data(data)

        reward_window.destroy()

        messagebox.showinfo(
            "成功",
            "獎勵已設定"
        )

    tk.Button(
        reward_window,
        text="儲存",
        bg="#444",
        fg="white",
        command=save_reward
    ).pack(pady=20)


# =========================
# GUI
# =========================

root = tk.Tk()

root.title("Professional Todo App")
root.geometry("1200x700")
root.configure(bg="#1e1e1e")


# =========================
# ttk 深色模式
# =========================

style = ttk.Style()

style.theme_use("default")

style.configure(
    "Treeview",
    background="#2b2b2b",
    foreground="white",
    rowheight=30,
    fieldbackground="#2b2b2b",
    bordercolor="#444",
    borderwidth=0
)

style.configure(
    "Treeview.Heading",
    background="#333",
    foreground="white",
    font=("Arial", 11, "bold")
)

style.map(
    "Treeview",
    background=[("selected", "#555")]
)


# =========================
# 左側
# =========================

left_frame = tk.Frame(
    root,
    bg="#1e1e1e"
)

left_frame.pack(
    side=tk.LEFT,
    fill=tk.Y,
    padx=10,
    pady=10
)

title = tk.Label(
    left_frame,
    text="Todo Lists",
    font=("Arial", 16),
    bg="#1e1e1e",
    fg="white"
)

title.pack(pady=10)

listbox_lists = tk.Listbox(
    left_frame,
    width=25,
    height=25,
    bg="#2b2b2b",
    fg="white",
    selectbackground="#555",
    exportselection=False
)

listbox_lists.pack()

listbox_lists.bind("<<ListboxSelect>>", show_tasks)

entry_list_name = tk.Entry(
    left_frame,
    width=22,
    bg="#333",
    fg="white",
    insertbackground="white"
)

entry_list_name.pack(pady=10)

btn_add_list = tk.Button(
    left_frame,
    text="新增清單",
    width=20,
    bg="#444",
    fg="white",
    command=add_todo_list
)

btn_add_list.pack(pady=5)

btn_delete_list = tk.Button(
    left_frame,
    text="刪除清單",
    width=20,
    bg="#444",
    fg="white",
    command=delete_todo_list
)

btn_delete_list.pack(pady=5)

btn_reward = tk.Button(
    left_frame,
    text="設定獎勵",
    width=20,
    bg="#444",
    fg="white",
    command=set_reward
)

btn_reward.pack(pady=5)


# =========================
# 右側
# =========================

right_frame = tk.Frame(
    root,
    bg="#1e1e1e"
)

right_frame.pack(
    side=tk.RIGHT,
    fill=tk.BOTH,
    expand=True,
    padx=10,
    pady=10
)

sort_frame = tk.Frame(
    right_frame,
    bg="#1e1e1e"
)

sort_frame.pack(pady=5)

tk.Label(
    sort_frame,
    text="排序方式：",
    bg="#1e1e1e",
    fg="white"
).pack(side=tk.LEFT, padx=5)

sort_mode_var = tk.StringVar(value="priority")

sort_combo = ttk.Combobox(
    sort_frame,
    textvariable=sort_mode_var,
    values=["priority", "deadline"],
    state="readonly",
    width=15
)

sort_combo.pack(side=tk.LEFT)

sort_combo.bind(
    "<<ComboboxSelected>>",
    show_tasks
)

tk.Label(
    sort_frame,
    text="排序演算法：",
    bg="#1e1e1e",
    fg="white"
).pack(side=tk.LEFT, padx=5)

sort_algorithm_var = tk.StringVar(value="timsort")

algorithm_combo = ttk.Combobox(
    sort_frame,
    textvariable=sort_algorithm_var,
    values=["timsort", "bubble", "heap"],
    state="readonly",
    width=15
)

algorithm_combo.pack(side=tk.LEFT)

algorithm_combo.bind(
    "<<ComboboxSelected>>",
    show_tasks
)

columns = (
    "status",
    "name",
    "deadline",
    "priority"
)

tree = ttk.Treeview(
    right_frame,
    columns=columns,
    show="headings",
    height=18
)

tree.heading("status", text="狀態")
tree.heading("name", text="任務名稱")
tree.heading("deadline", text="截止時間")
tree.heading("priority", text="優先級")

tree.column("status", width=80, anchor="center")
tree.column("name", width=350)
tree.column("deadline", width=200)
tree.column("priority", width=100, anchor="center")

tree.pack(fill=tk.BOTH, expand=True)

tree.bind("<Double-1>", edit_task)

# 彩色優先級

tree.tag_configure(
    "high",
    background="#5c1f1f",
    foreground="#ffb3b3"
)

tree.tag_configure(
    "medium",
    background="#5c4b1f",
    foreground="#ffe599"
)

tree.tag_configure(
    "low",
    background="#1f5c2e",
    foreground="#b6fcb6"
)

tree.tag_configure(
    "completed",
    background="#333333",
    foreground="#888888"
)

# Scrollbar

scrollbar = ttk.Scrollbar(
    right_frame,
    orient="vertical",
    command=tree.yview
)

tree.configure(
    yscrollcommand=scrollbar.set
)

scrollbar.pack(
    side=tk.RIGHT,
    fill=tk.Y
)


# =========================
# 輸入區
# =========================

input_frame = tk.Frame(
    right_frame,
    bg="#1e1e1e"
)

input_frame.pack(pady=10)

entry_task_name = tk.Entry(
    input_frame,
    width=30,
    bg="#333",
    fg="white",
    insertbackground="white"
)

entry_task_name.grid(row=0, column=0, padx=5)
entry_task_name.insert(0, "任務名稱")

entry_deadline = tk.Entry(
    input_frame,
    width=25,
    bg="#333",
    fg="white",
    insertbackground="white"
)

entry_deadline.grid(row=0, column=1, padx=5)
entry_deadline.insert(0, "2026-05-10 18:00")

entry_priority = tk.Entry(
    input_frame,
    width=10,
    bg="#333",
    fg="white",
    insertbackground="white"
)

entry_priority.grid(row=0, column=2, padx=5)
entry_priority.insert(0, "3")


# =========================
# 按鈕區
# =========================

button_frame = tk.Frame(
    right_frame,
    bg="#1e1e1e"
)

button_frame.pack(pady=10)

btn_add_task = tk.Button(
    button_frame,
    text="新增任務",
    width=15,
    bg="#444",
    fg="white",
    command=add_task
)

btn_add_task.grid(row=0, column=0, padx=5)

btn_complete = tk.Button(
    button_frame,
    text="標記完成",
    width=15,
    bg="#444",
    fg="white",
    command=complete_task
)

btn_complete.grid(row=0, column=1, padx=5)

btn_delete = tk.Button(
    button_frame,
    text="刪除任務",
    width=15,
    bg="#444",
    fg="white",
    command=delete_task
)

btn_delete.grid(row=0, column=2, padx=5)


# =========================
# 初始化
# =========================

refresh_lists()

# =========================
# 啟動
# =========================

root.mainloop()