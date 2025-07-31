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


def parse_file(filepath):
    with open(filepath, 'r') as f:
        file_content = f.read()
    parts = file_content.split("---",2)
    page_config = yaml.safe_load(parts[1])
    markdown_data = parts[2]

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
        page_data['url'] = '/' + output_filename

        render_page(page_data, html_content, site_config, templates)
    else:
        print("Running a full build...")        
        pages = []
        for filename in os.listdir(CONTENT_DIR):
            if filename.endswith('.md'):
                filepath = os.path.join(CONTENT_DIR, filename)
                page_data, html_content = parse_file(filepath)
                pages.append({'data': page_data, 'content': html_content})

        all_posts = [p['data'] for p in pages if p['data'].get('layout') == 'post']
        all_posts.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)
        
        for page in pages:
            render_page(page['data'], page['content'], site_config, templates, all_posts)

if __name__ == "__main__":
    main()
# with open(CONFIG_FILE, 'r') as f:
#     site_config = yaml.safe_load(f)

# env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

# templates = {
#     "main": env.get_template('main.html'),
#     "post": env.get_template('post.html'),
#     "blog": env.get_template('blog.html')
# }

# allposts = []

# for file in os.listdir(CONTENT_DIR):
#     if not file.endswith(".md"):
#         continue
#     filepath = os.path.join(CONTENT_DIR, file)

#     with open(filepath, 'r') as f:
#         file_content = f.read()
#     parts = file_content.split("---",2)
#     page_config = yaml.safe_load(parts[1])
#     markdown_data = parts[2]    

#     html_data = markdown.markdown(markdown_data)
#     layout = page_config.get('layout')
#     template = templates[layout]

#     final_html = template.render(
#         site = site_config,
#         page = page_config,
#         content = html_data
#     )

#     output_filename = os.path.splitext(file)[0] + '.html'

#     page_config['url'] = '/' + output_filename
#     if page_config.get('layout') == 'post':
#         allposts.append(page_config)
#     if layout == 'blog':
#         allposts.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)
#         final_html = template.render(site=site_config, page=page_config, posts=allposts)
#     else:
#         final_html = template.render(site=site_config, page=page_config, content=html_data)
#     output_path = os.path.join(OUTPUT_DIR, output_filename)
#     with open(output_path, 'w') as f:
#         f.write(final_html)
#     print(f"converted {file} to html")