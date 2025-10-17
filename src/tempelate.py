

import jinja2
import os


def render_page(page_config, html_data, site_config, templates, all_posts=None, OUTPUT_DIR='.'):
    layout = page_config.get("layout")
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getenv("TEMPLATE_DIR", "templates")))
    try:
        template = env.get_template(f'{layout}.html')
    except jinja2.exceptions.TemplateNotFound:
        print(f'Template {layout}.html not found. Skipping build')
        return
    if layout not in templates:
        print("Error: Template not found. Skipping build.")
        return    
    
    
    layout = page_config.get("layout")


    render_details = {"site": site_config, "page": page_config, "content": html_data}
    if layout == "blog" and all_posts is not None:
        render_details["posts"] = all_posts

    final_html = template.render(render_details)

    output_path = os.path.join(OUTPUT_DIR, page_config["url"].lstrip("/"), "index.html")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(final_html)
    print(f"Generated: {page_config['url']}")
