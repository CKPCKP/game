import json
import os

SAVE_DIR = "saves"
SLOT_COUNT = 3


def ensure_save_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)


def list_slots():
    """スロットごとのデータを None or dict で返す"""
    ensure_save_dir()
    slots = []
    for i in range(SLOT_COUNT):
        path = os.path.join(SAVE_DIR, f"slot_{i}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                slots.append(json.load(f))
        else:
            slots.append(None)
    return slots


def save_slot(slot_index, data):
    ensure_save_dir()
    path = os.path.join(SAVE_DIR, f"slot_{slot_index}.json")
    with open(path, "w") as f:
        json.dump(data, f)


def load_slot(slot_index):
    path = os.path.join(SAVE_DIR, f"slot_{slot_index}.json")
    with open(path, "r") as f:
        return json.load(f)


def delete_slot(slot_index):
    path = os.path.join(SAVE_DIR, f"slot_{slot_index}.json")
    if os.path.exists(path):
        os.remove(path)
