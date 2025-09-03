import os
import yaml
import markdown
from markdown.extensions.toc import TocExtension
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import argparse
import shutil
import hashlib
import json
import re

TEMPLATE_DIR = "templates"
CONFIG_FILE = "config.yaml"
OUTPUT_DIR = "."
IMAGES_DIR = "assets/images"
CONTENT_DIR = "content"
POSTS_DIR = "content/posts"

PAGE_SLUG_CACHE = ".cache/page-slugs.json"
IMAGE_MANIFEST_PATH = ".cache/image-manifest.json"

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

def clean_output(directory):
    print("Cleaning old build files...")
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename == 'index.html' or filename.endswith('.xml'):
                file_path = os.path.join(root, filename)
                os.remove(file_path)
                print(f"Deleted: {file_path}")

    posts_dir_path = os.path.join(directory, 'posts')
    tags_dir_path = os.path.join(directory, 'tags')
    if os.path.exists(posts_dir_path):
        shutil.rmtree(posts_dir_path)
        print(f"Deleted directory: {posts_dir_path}")
    if os.path.exists(tags_dir_path):
        shutil.rmtree(tags_dir_path)
        print(f"Deleted directory: {tags_dir_path}")

def has_file_changed(filepath, cache_dir=".cache"):
    os.makedirs(cache_dir, exist_ok=True)
    rel = os.path.relpath(filepath)
    file_hash = hashlib.md5(open(filepath, 'rb').read()).hexdigest()
    safe_name = rel.replace(os.sep, '__') + '.hash'
    cache_file = os.path.join(cache_dir, safe_name)

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cached_hash = f.read().strip()
        if cached_hash == file_hash:
            return False

    with open(cache_file, 'w') as f:
        f.write(file_hash)
    return True

MARKDOWN_EXTENSIONS = [
    "fenced_code",
    "codehilite",
    "footnotes",
    "tables",
    "attr_list",
    "sane_lists",
    "md_in_html",
    TocExtension(permalink=True)
]

MARKDOWN_EXTENSION_CONFIGS = {
    "codehilite": {
        "guess_lang": False,
        "noclasses": False,   # produce CSS classes (preferable with a pygments CSS)
        "pygments_style": "native"
    },
}

def build_markdown():
    return markdown.Markdown(
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=MARKDOWN_EXTENSION_CONFIGS
    )

def parse_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        return None, None

    if file_content.startswith('---'):
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

    # Image substitution before markdown conversion
    markdown_data = replace_md_images(markdown_data)

    md = build_markdown()
    html_data = md.convert(markdown_data)
    md.reset()

    slug = os.path.splitext(os.path.basename(filepath))[0]
    rel_posts = os.path.normpath(POSTS_DIR)
    if os.path.normpath(filepath).startswith(rel_posts):
        page_config['url'] = f'/posts/{slug}'
    elif slug == 'index':
        page_config['url'] = '/'
    else:
        page_config['url'] = f'/{slug}'

    # Normalize date to YYYY-MM-DD string if provided
    if 'date' in page_config and page_config['date']:
        if isinstance(page_config['date'], datetime):
            page_config['date'] = page_config['date'].strftime('%Y-%m-%d')
        else:
            # Try parse loose formats
            try:
                parsed = datetime.fromisoformat(str(page_config['date']))
                page_config['date'] = parsed.strftime('%Y-%m-%d')
            except Exception:
                pass

    return page_config, html_data

def tag_pages(tag_template, site_config, tags ={}):
    tags_dir = os.path.join(OUTPUT_DIR, 'tags')
    os.makedirs(tags_dir, exist_ok=True)

    for tag_name, posts_with_tag in tags.items():
            posts_with_tag.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)
            tag_page_html = tag_template.render(
                site=site_config,
                tag_name=tag_name,
                posts=posts_with_tag,
                page={'title': f'Tag: {tag_name}'}
            )
            output_path = os.path.join(tags_dir, f'{tag_name}.html')
            with open(output_path, 'w') as f:
                f.write(tag_page_html)
            print(f"Generated tag page: tags/{tag_name}.html")

def render_page(page_config, html_data, site_config, templates, all_posts=None):
    layout = page_config.get('layout')
    if layout not in templates:
        print("Error: Template not found. Skipping build.")
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

    if page_config['url'] == '/':
        output_path = os.path.join(OUTPUT_DIR, 'index.html')
    else:
        output_path = os.path.join(OUTPUT_DIR, page_config['url'].lstrip('/'), 'index.html')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(final_html)
    print(f"Generated: {page_config['url'] if page_config['url'] != '/' else '/index.html'}")

def load_image_manifest():
    try:
        with open(IMAGE_MANIFEST_PATH, "r") as f:
            return json.load(f)
    except:
        return {}

IMAGE_MANIFEST = load_image_manifest()
IMAGE_TAG_RE = re.compile(r'!\[(?P<alt>[^\]]*)\]\((?P<src>assets/images/[^)]+)\)')

def replace_md_images(md_text):
    def repl(m):
        alt = m.group('alt')
        src = m.group('src')
        fname = src.split('/')[-1]
        variants = IMAGE_MANIFEST.get(fname)
        if not variants:
            return f'![{alt}]({src})'
        # webp > avif > jpg 
        primary = (variants.get('webp') or variants.get('avif') or variants.get('jpg'))[0]
        sources_html = []
        order = ['avif','webp','jpg']
        for fmt in order:
            if fmt in variants:
                srcset = ", ".join(f"{v['path']} {v['width']}w" for v in variants[fmt])
                sources_html.append(
                    f'<source type="image/{("jpeg" if fmt=="jpg" else fmt)}" srcset="{srcset}" sizes="100vw">'
                )
        fallback_path = primary['path']
        return (
          f'<picture>{"".join(sources_html)}'
          f'<img src="{fallback_path}" alt="{alt}" loading="lazy" decoding="async" />'
          f'</picture>'
        )
    return IMAGE_TAG_RE.sub(repl, md_text)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file')
    parser.add_argument('--clean', action='store_true')
    args = parser.parse_args()

    if args.clean:
        clean_output(OUTPUT_DIR)
        if os.path.exists(PAGE_SLUG_CACHE):
            os.remove(PAGE_SLUG_CACHE)
        print("generated files are deleted.")
        return

    with open(CONFIG_FILE, 'r') as f:
        site_config = yaml.safe_load(f)
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    templates = {
        "main": env.get_template('main.html'),
        "blog": env.get_template('blog.html'),
        "post": env.get_template('post.html'),
        "tags": env.get_template('tags.html')
    }

    if args.file:
        print(f"Change detected in {args.file}, proceeding to rebuild...")
        if not os.path.exists(args.file):

            slug = os.path.splitext(os.path.basename(args.file))[0]
            if slug != 'index':
                out_dir = os.path.join(OUTPUT_DIR, slug)
                if os.path.isdir(out_dir):
                    shutil.rmtree(out_dir)
                    print(f"Removed deleted page output: {out_dir}")
            
            if os.path.exists(PAGE_SLUG_CACHE):
                os.remove(PAGE_SLUG_CACHE)
            return

        if not has_file_changed(args.file):
            print(f"No changes detected in {args.file}. Skipping rebuild.")
            return

        page_data, html_content = parse_file(args.file)
        if page_data is None or html_content is None:
            return
        render_page(page_data, html_content, site_config, templates)
    else:
        print("Running a full build...")
        sitemap_list = []
        all_posts = []
        pages = []
        tags = {}

        clean_output(OUTPUT_DIR)

        current_slugs = set()
        previous_slugs = load_previous_slugs()

        for filename in os.listdir(CONTENT_DIR):
            if filename.endswith('.md'):
                filepath = os.path.join(CONTENT_DIR, filename)
                page_data, html_content = parse_file(filepath)
                if not page_data:
                    continue
                if str(page_data.get('draft')).lower() in ('true', '1', 'yes'):
                    continue
                slug = os.path.splitext(filename)[0]
                current_slugs.add(slug)
                pages.append({'data': page_data, 'content': html_content})
                sitemap_list.append(page_data['url'])

        if os.path.exists(POSTS_DIR):
            for filename in os.listdir(POSTS_DIR):
                if filename.endswith('.md'):
                    filepath = os.path.join(POSTS_DIR, filename)
                    page_data, html_content = parse_file(filepath)
                    if not page_data:
                        continue
                    if str(page_data.get('draft')).lower() in ('true', '1', 'yes'):
                        continue
                    slug = os.path.splitext(filename)[0]
                    current_slugs.add(f"posts/{slug}")
                    pages.append({'data': page_data, 'content': html_content})
                    sitemap_list.append(page_data['url'])
                    if page_data.get('layout') == 'post':
                        all_posts.append(page_data)
                        for tag in page_data.get('tags') or []:
                            tags.setdefault(tag, []).append(page_data)

        removed = previous_slugs - current_slugs
        for slug in removed:
            
            if slug.startswith('posts/'):
                continue
            if slug == 'index':
                continue
            out_dir = os.path.join(OUTPUT_DIR, slug)
            if os.path.isdir(out_dir):
                shutil.rmtree(out_dir)
                print(f"Removed stale page directory: {out_dir}")

        save_current_slugs(current_slugs)

        all_posts.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d') if x.get('date') else datetime.min, reverse=True)
        for page in pages:
            render_page(page['data'], page['content'], site_config, templates, all_posts)

        tag_pages(templates['tags'], site_config, tags)

        sitemap_template = env.get_template('sitemap.xml.j2')
        sitemap_xml = sitemap_template.render(
            site=site_config,
            pages=sitemap_list
        )
        with open(os.path.join(OUTPUT_DIR, 'sitemap.xml'), 'w') as f:
            f.write(sitemap_xml)
        print("Generated sitemap.xml")

if __name__ == "__main__":
    main()