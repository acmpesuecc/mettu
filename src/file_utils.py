import os
import hashlib
import shutil
import json

def clean_output(directory):
    print("Cleaning old build files...")
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename == "index.html" or filename.endswith(".xml"):
                file_path = os.path.join(root, filename)
                os.remove(file_path)
                print(f"Deleted: {file_path}")
    
    remove_directory(directory, "posts")
    remove_directory(directory, "tags")


def remove_directory(directory, subdir):
    dir_path = os.path.join(directory, subdir)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
        print(f"Deleted directory: {dir_path}")


def has_file_changed(filepath, cache_dir=".cache"):
    os.makedirs(cache_dir, exist_ok=True)
    rel = os.path.relpath(filepath)
    file_hash = hashlib.md5(open(filepath, "rb").read()).hexdigest()
    safe_name = rel.replace(os.sep, "__") + ".hash"
    cache_file = os.path.join(cache_dir, safe_name)

    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            cached_hash = f.read().strip()
        if cached_hash == file_hash:
            return False

    with open(cache_file, "w") as f:
        f.write(file_hash)
    return True


def load_previous_slugs(cache_file=".cache/page-slugs.json"):
    try:
        with open(cache_file, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


def save_current_slugs(slugs, cache_file=".cache/page-slugs.json"):
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump(sorted(slugs), f)
