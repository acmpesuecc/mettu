

import os
import dotenv
import yaml

dotenv.load_dotenv()

PYGMENTIZE_THEME = os.getenv("PYGMENTIZE_THEME", "native")
TEMPLATE_DIR = os.getenv("TEMPLATE_DIR", "templates")
CONFIG_FILE = os.getenv("CONFIG_FILE", "config.yaml")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", ".")
IMAGES_DIR = os.getenv("IMAGES_DIR", "assets/images")
CONTENT_DIR = os.getenv("CONTENT_DIR", "content")
POSTS_DIR = os.getenv("POSTS_DIR", "content/posts")
PAGE_SLUG_CACHE = ".cache/page-slugs.json"


def loaf_config():
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)
