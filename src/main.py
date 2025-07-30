import os
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = "templates"
CONFIG_FILE = "config.yaml"
OUTPUT_DIR = "."
IMAGES_DIR = "assets/images"
CONTENT_DIR = "content"

with open(CONFIG_FILE, 'r') as f:
    site_config = yaml.safe_load(f)

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

templates = {
    "main": env.get_template('main.html'),
    # "blog_post": env.get_template('blog_post.html'),
    # "blog_link_stash": env.get_template('blog_link_statsh.html')
}

for file in os.listdir(CONTENT_DIR):
    if not file.endswith(".md"):
        continue
    filepath = os.path.join(CONTENT_DIR, file)

    with open(filepath, 'r') as f:
        file_content = f.read()
    parts = file_content.split("---",2)
    page_config = yaml.safe_load(parts[1])
    markdown_data = parts[2]

    html_data = markdown.markdown(markdown_data)
    layout = page_config.get('layout')
    template = templates[layout]

    final_html = template.render(
        site = site_config,
        page = page_config,
        content = html_data
    )

    output_filename = os.path.splitext(file)[0] + '.html'
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, 'w') as f:
        f.write(final_html)
    print(f"converted {file} to html")