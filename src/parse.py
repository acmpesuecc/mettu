import markdown
from markdown.extensions.toc import TocExtension
import yaml
from datetime import datetime
import os

MARKDOWN_EXTENSIONS = [
    "fenced_code",
    "codehilite",
    "footnotes",
    "tables",
    "attr_list",
    "sane_lists",
    "md_in_html",
    TocExtension(permalink=True),
]

MARKDOWN_EXTENSION_CONFIGS = {
    "codehilite": {
        "guess_lang": False,
        "noclasses": False,
    },
}


def build_markdown():
    return markdown.Markdown(
        extensions=MARKDOWN_EXTENSIONS, extension_configs=MARKDOWN_EXTENSION_CONFIGS
    )


def parse_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            file_content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        return None, None

    if file_content.startswith("---"):
        try:
            parts = file_content.split("---", 2)
            page_config = yaml.safe_load(parts[1]) or {}
            markdown_data = parts[2]
        except (IndexError, yaml.YAMLError) as e:
            print(f"Error parsing YAML frontmatter in {filepath}: {e}")
            page_config = {}
            markdown_data = file_content
    else:
        page_config = {}
        markdown_data = file_content

    md = build_markdown()
    html_data = md.convert(markdown_data)
    md.reset()

    slug = os.path.splitext(os.path.basename(filepath))[0]
    page_config["url"] = f"/{slug}" if slug != "index" else "/"

    # Normalize date to YYYY-MM-DD string
    if "date" in page_config and page_config["date"]:
        page_config["date"] = normalize_date(page_config["date"])

    return page_config, html_data


def normalize_date(date):
    if isinstance(date, datetime):
        return date.strftime("%Y-%m-%d")
    else:
        try:
            parsed = datetime.fromisoformat(str(date))
            return parsed.strftime("%Y-%m-%d")
        except Exception:
            return None
