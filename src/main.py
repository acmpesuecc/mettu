import os
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import argparse

TEMPLATE_DIR = "templates"
CONFIG_FILE = "config.yaml"
OUTPUT_DIR = "."
IMAGES_DIR = "assets/images"
CONTENT_DIR = "content"
POSTS_DIR = "content/posts"


def parse_file(filepath):
    with open(filepath, 'r') as f:
        file_content = f.read()
    
    if file_content.startswith('---'):
        try:
            parts = file_content.split("---", 2)
            page_config = yaml.safe_load(parts[1])
            markdown_data = parts[2]
        except (IndexError, yaml.YAMLError):
            page_config = {}
            markdown_data = file_content
    else:
        page_config = {}
        markdown_data = file_content

    if page_config is None:
        page_config = {}

    # html_data = markdown.markdown(markdown_data)
    # parts = file_content.split("---",2)
    # page_config = yaml.safe_load(parts[1])
    # markdown_data = parts[2]

    html_data = markdown.markdown(markdown_data)
    output_filename = os.path.splitext(os.path.basename(filepath))[0] + '.html'
    page_config['url'] = f'/{output_filename}'

    return page_config, html_data

def render_page(page_config, html_data, site_config, templates, all_posts=None):
    layout = page_config.get('layout')
    if layout not in templates:
        print("template not found. Skipped build.")
        return
    
    template = templates[layout]

    render_details = {
        "site": site_config,
        "page": page_config,
        "content": html_data
    }
    if layout == 'blog' and all_posts is not None:
        render_details['posts'] = all_posts
    final_html = template.render(render_details)
    output_path = os.path.join(OUTPUT_DIR, page_config['url'].lstrip('/'))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(final_html)
    print(f"Generated: {os.path.basename(output_path)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file')
    args = parser.parse_args()

    with open(CONFIG_FILE, 'r') as f:
        site_config = yaml.safe_load(f)
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    templates = {
        "main": env.get_template('main.html'),
        "blog": env.get_template('blog.html'),
        "post": env.get_template('post.html')
    }

    if args.file:
        print(f"rebuilding {args.file}...")
        
        page_data, html_content = parse_file(args.file)
        output_filename = os.path.splitext(os.path.basename(args.file))[0] + '.html'

        if 'posts' in args.file:
            page_data['url'] = f'/posts/{output_filename}'
        else:
            page_data['url'] = f'/{output_filename}'

        render_page(page_data, html_content, site_config, templates)

    else:
        print("Running a full build...")
        all_posts = []
        pages = []

        for filename in os.listdir(CONTENT_DIR):
            if filename.endswith('.md'):
                filepath = os.path.join(CONTENT_DIR, filename)
                page_data, html_content = parse_file(filepath)
                pages.append({'data': page_data, 'content': html_content})

        if os.path.exists(POSTS_DIR):
            for filename in os.listdir(POSTS_DIR):
                if filename.endswith('.md'):
                    filepath = os.path.join(POSTS_DIR, filename)
                    page_data, html_content = parse_file(filepath)

                    output_filename = os.path.splitext(filename)[0] + '.html'
                    page_data['url'] = f'/posts/{output_filename}'

                    pages.append({'data': page_data, 'content': html_content})
                    if page_data.get('layout') == 'post':
                        all_posts.append(page_data)
        
        all_posts.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)
        for page in pages:
            render_page(page['data'], page['content'], site_config, templates, all_posts)

if __name__ == "__main__":
    main()