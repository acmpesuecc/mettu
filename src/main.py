import os
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

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
    "post": env.get_template('post.html'),
    "blog": env.get_template('blog.html')
}

allposts = []

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

    page_config['url'] = '/' + output_filename
    if page_config.get('layout') == 'post':
        allposts.append(page_config)
    if layout == 'blog':
        allposts.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)
        final_html = template.render(site=site_config, page=page_config, posts=allposts)
    else:
        final_html = template.render(site=site_config, page=page_config, content=html_data)
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, 'w') as f:
        f.write(final_html)
    print(f"converted {file} to html")