import os
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") == "True" else logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

FOOTER_START = "<!-- FooterStart -->"
FOOTER_END = "<!-- FooterEnd -->"
FOOTER_SKIP = "<!-- FooterSkip -->"


def find_readme_files(root_dir):
    logging.debug(f"Searching for README files in: {root_dir}")
    readme_files = []
    root_readme = None

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower() == "readme.md":
                path = os.path.join(root, file)
                logging.debug(f"Found README file: {path}")

                # Skip any README files that contain the skip marker
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()

                if FOOTER_SKIP in content:
                    logging.debug(f"Skipping {path} due to FooterSkip marker")
                    continue

                # If this is the root README.md, store it separately
                if os.path.dirname(path) == root_dir:
                    root_readme = path
                else:
                    readme_files.append(path)

    # Sort the non-root README files
    readme_files.sort()

    # If we found a root README, insert it at the beginning
    if root_readme:
        readme_files.insert(0, root_readme)
        logging.debug(f"Root README found and placed first: {root_readme}")

    logging.debug(f"Total README files found: {len(readme_files)}")
    return readme_files


def get_title_from_file(file_path):
    logging.debug(f"Getting title from file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("# "):
                title = line.strip("# ").strip()
                logging.debug(f"Found title: {title}")
                return title
    logging.debug("No title found, using default 'README'")
    return "README"


def content_changed(file_path, new_content):
    with open(file_path, "r", encoding="utf-8") as file:
        old_content = file.read()
    changed = old_content.strip() != new_content.strip()
    logging.debug(f"Content changed for {file_path}: {changed}")
    return changed


def update_footer_links(readme_files):
    logging.debug(f"Starting to update footer links for {len(readme_files)} files")

    for i, file_path in enumerate(readme_files):
        current_file_title = get_title_from_file(file_path)
        logging.debug(f"Processing file {i + 1}/{len(readme_files)}: {file_path}")
        logging.debug(f"Current file title: {current_file_title}")

        # Skip previous link for root README.md
        prev_file_title = None if i == 0 else get_title_from_file(readme_files[i - 1])
        next_file_title = (
            get_title_from_file(readme_files[0])
            if i == len(readme_files) - 1
            else get_title_from_file(readme_files[i + 1])
        )
        logging.debug(f"Previous file title: {prev_file_title}")
        logging.debug(f"Next file title: {next_file_title}")

        # Read the file and split its content to remove the existing footer
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        if FOOTER_SKIP in content:
            logging.debug(f"Skipping {file_path} due to FooterSkip marker")
            continue

        if FOOTER_START in content:
            content, _ = re.split(rf"{re.escape(FOOTER_START)}", content, 1)

        # Prepare the new footer
        footer = f"\n\n{FOOTER_START}\n---\n"
        links = []

        if prev_file_title:
            prev_link = os.path.relpath(readme_files[i - 1], os.path.dirname(file_path))
            links.append(f"[← {prev_file_title}]({prev_link})")
            logging.debug(f"Added previous link: {prev_link}")

        if next_file_title:
            next_link = (
                os.path.relpath(readme_files[0], os.path.dirname(file_path))
                if i == len(readme_files) - 1
                else os.path.relpath(readme_files[i + 1], os.path.dirname(file_path))
            )
            links.append(f"[{next_file_title} →]({next_link})")
            logging.debug(f"Added next link: {next_link}")

        footer += " | ".join(links) + f"\n{FOOTER_END}\n"
        logging.debug(f"Generated footer: {footer}")

        new_content = content.strip() + footer

        # Write the updated content with the new footer back to the file
        # but only if changes are detected
        if content_changed(file_path, new_content):
            logging.debug(f"Writing changes to {file_path}")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)
        else:
            logging.debug(f"No changes needed for {file_path}")


if __name__ == "__main__":
    root_directory = os.getenv("PROJECT_HOME", os.getcwd())
    logging.debug(f"Starting script with root directory: {root_directory}")
    readme_files = find_readme_files(root_directory)
    update_footer_links(readme_files)
