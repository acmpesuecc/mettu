import argparse
import jinja2
import os
import shutil
from config import loaf_config
from file_utils import clean_output, has_file_changed, load_previous_slugs, save_current_slugs
from parse import parse_file
from tempelate import render_page
from tags import tag_pages
from datetime import datetime
from slug import load_previous_slugs, save_current_slugs
from bs4 import BeautifulSoup

def process_images_in_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    images = soup.find_all('img')
    processed_dir_web_path = '/assets/images-processed'
    generated_widths = [400, 800, 1200]
    for img in images:
        original_src = img.get('src')
        # Only process images from the original assets directory
        if original_src and original_src.startswith('/assets/images/'):
            try:
                base_path = original_src.replace('/assets/images/', '')
                filename_no_ext, original_ext = os.path.splitext(base_path)
                srcset_parts = []
                for width in generated_widths:
                    processed_filename = f"{filename_no_ext}-{width}w.webp"
                    processed_src = f"{processed_dir_web_path}/{processed_filename}"
                    srcset_parts.append(f"{processed_src} {width}w")
                if srcset_parts:
                    img['srcset'] = ", ".join(srcset_parts)
                    img['sizes'] = "(max-width: 800px) 90vw, 800px"
                    img['src'] = f"{processed_dir_web_path}/{filename_no_ext}-{generated_widths[1]}w.webp" # use 800w as default
                else:
                    print(f"Warning: No processed images found for {original_src}")
            except Exception as e:
                print(f"Error processing image {original_src}: {e}")
    return str(soup)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Rebuild a specific file if changed.")
    parser.add_argument("--clean", action="store_true", help="Clean the output directory.")
    args = parser.parse_args()
    if args.clean:
        clean_output(os.getenv("OUTPUT_DIR", "."))
        if os.path.exists(os.getenv("PAGE_SLUG_CACHE", ".cache/page-slugs.json")):
            os.remove(os.getenv("PAGE_SLUG_CACHE", ".cache/page-slugs.json"))
        print("Generated files are deleted.")
        return
    site_config = loaf_config()
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getenv("TEMPLATE_DIR", "templates")))
    templates = {
        "main": env.get_template("main.html"),
        "blog": env.get_template("blog.html"),
        "post": env.get_template("post.html"),
        "tags": env.get_template("tags.html"),
    }

    if args.file:
        print(f"Change detected in {args.file}, proceeding to rebuild...")
        if not os.path.exists(args.file):
            slug = os.path.splitext(os.path.basename(args.file))[0]
            if slug != "index":
                out_dir = os.path.join(os.getenv("OUTPUT_DIR", "."), slug)
                if os.path.isdir(out_dir):
                    shutil.rmtree(out_dir)
                    print(f"Removed deleted page output: {out_dir}")
            if os.path.exists(os.getenv("PAGE_SLUG_CACHE", ".cache/page-slugs.json")):
                os.remove(os.getenv("PAGE_SLUG_CACHE", ".cache/page-slugs.json"))
            return
        if not has_file_changed(args.file):
            print(f"No changes detected in {args.file}. Skipping rebuild.")
            return
        page_data, html_content = parse_file(args.file)
        if page_data is None or html_content is None:
            return
        final_html = process_images_in_html(html_content)
        render_page(page_data, final_html, site_config, templates)
    else:
        print("Running a full build...")
        sitemap_list = []
        all_posts = []
        pages = []
        tags = {}
        clean_output(os.getenv("OUTPUT_DIR", "."))
        current_slugs = set()
        previous_slugs = load_previous_slugs()
        for filename in os.listdir(os.getenv("CONTENT_DIR", "content")):
            if filename.endswith(".md"):
                filepath = os.path.join(os.getenv("CONTENT_DIR", "content"), filename)
                page_data, html_content = parse_file(filepath)
                if not page_data:
                    continue
                if str(page_data.get("draft")).lower() in ("true", "1", "yes"):
                    continue
                slug = os.path.splitext(filename)[0]
                current_slugs.add(slug)
                final_html = process_images_in_html(html_content)
                pages.append({"data": page_data, "content": final_html})
                sitemap_list.append(page_data["url"])
        if os.path.exists(os.getenv("POSTS_DIR", "content/posts")):
            for filename in os.listdir(os.getenv("POSTS_DIR", "content/posts")):
                if filename.endswith(".md"):
                    filepath = os.path.join(os.getenv("POSTS_DIR", "content/posts"), filename)
                    page_data, html_content = parse_file(filepath)
                    if not page_data:
                        continue
                    if str(page_data.get("draft")).lower() in ("true", "1", "yes"):
                        continue
                    slug = os.path.splitext(filename)[0]
                    current_slugs.add(f"posts/{slug}")
                    final_html = process_images_in_html(html_content)
                    pages.append({"data": page_data, "content": final_html})
                    sitemap_list.append(page_data["url"])
                    if page_data.get("layout") == "post":
                        all_posts.append(page_data)
                    for tag in page_data.get("tags") or []:
                        tags.setdefault(tag, []).append(page_data)
        removed = previous_slugs - current_slugs
        for slug in removed:
            if slug.startswith("posts/"):
                continue
            if slug == "index":
                continue
            out_dir = os.path.join(os.getenv("OUTPUT_DIR", "."), slug)
            if os.path.isdir(out_dir):
                shutil.rmtree(out_dir)
                print(f"Removed stale page directory: {out_dir}")
        save_current_slugs(current_slugs)
        all_posts.sort(
            key=lambda x: (
                datetime.strptime(x["date"], "%Y-%m-%d")
                if x.get("date")
                else datetime.min
            ),
            reverse=True,
        )
        for page in pages:
            render_page(page["data"], page["content"], site_config, templates, all_posts)
        tag_pages(templates["tags"], site_config, tags)
        sitemap_template = env.get_template("sitemap.xml.j2")
        sitemap_xml = sitemap_template.render(site=site_config, pages=sitemap_list)
        with open(os.path.join(os.getenv("OUTPUT_DIR", "."), "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write(sitemap_xml)
        print("Generated sitemap.xml")

if __name__ == "__main__":
    main()
