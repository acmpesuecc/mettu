import os
from datetime import datetime



def tag_pages(tag_template, site_config, tags={},OUTPUT_DIR='.'):
    tags_dir = os.path.join(OUTPUT_DIR, "tags")
    os.makedirs(tags_dir, exist_ok=True)

    for tag_name, posts_with_tag in tags.items():
        posts_with_tag.sort(
            key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"), reverse=True
        )
        tag_page_html = tag_template.render(
            site=site_config,
            tag_name=tag_name,
            posts=posts_with_tag,
            page={"title": f"Tag: {tag_name}"},
        )
        output_path = os.path.join(tags_dir, f"{tag_name}.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(tag_page_html)
        print(f"Generated tag page: tags/{tag_name}.html")
