import os
import re


FOOTER_START = "<!-- FooterStart -->"
FOOTER_END = "<!-- FooterEnd -->"
FOOTER_SKIP = "<!-- FooterSkip -->"


def find_readme_files(root_dir):
    readme_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower() == "readme.md":
                path = os.path.join(root, file)

                # Skip any README files that contain the skip marker
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()

                if FOOTER_SKIP in content:
                    continue

                readme_files.append(path)

    readme_files.sort()
    return readme_files


def get_title_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("# "):
                return line.strip("# ").strip()
    return "README"


def content_changed(file_path, new_content):
    with open(file_path, "r", encoding="utf-8") as file:
        old_content = file.read()
    return old_content.strip() != new_content.strip()


def update_footer_links(readme_files):
    for i, file_path in enumerate(readme_files):

        current_file_title = get_title_from_file(file_path)
        print(f"\tProcessing: {current_file_title}")

        prev_file_title = get_title_from_file(readme_files[i - 1]) if i > 0 else None
        next_file_title = (
            get_title_from_file(readme_files[0])
            if i == len(readme_files) - 1
            else get_title_from_file(readme_files[i + 1])
        )

        # Read the file and split its content to remove the existing footer
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        if FOOTER_SKIP in content:
            continue

        if FOOTER_START in content:
            content, _ = re.split(rf"{re.escape(FOOTER_START)}", content, 1)

        # Prepare the new footer
        footer = f"\n\n{FOOTER_START}\n---\n"
        links = []

        if prev_file_title:
            prev_link = os.path.relpath(readme_files[i - 1], os.path.dirname(file_path))
            links.append(f"[← {prev_file_title}]({prev_link})")

        if next_file_title:
            next_link = (
                os.path.relpath(readme_files[0], os.path.dirname(file_path))
                if i == len(readme_files) - 1
                else os.path.relpath(readme_files[i + 1], os.path.dirname(file_path))
            )
            links.append(f"[{next_file_title} →]({next_link})")

        footer += " | ".join(links) + f"\n{FOOTER_END}\n"

        new_content = content.strip() + footer

        # Write the updated content with the new footer back to the file
        # but only if changes are detected
        if content_changed(file_path, new_content):
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)


if __name__ == "__main__":
    root_directory = os.getenv("PROJECT_HOME", os.getcwd())
    readme_files = find_readme_files(root_directory)
    update_footer_links(readme_files)
