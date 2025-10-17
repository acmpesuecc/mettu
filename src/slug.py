import json
import os

PAGE_SLUG_CACHE = ".cache/page-slugs.json"


def load_previous_slugs():
    try:
        with open(PAGE_SLUG_CACHE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_current_slugs(slugs):
    os.makedirs(os.path.dirname(PAGE_SLUG_CACHE), exist_ok=True)
    with open(PAGE_SLUG_CACHE, "w") as f:
        json.dump(sorted(slugs), f)
