import io
import logging
import os
import zipfile

import requests

logger = logging.getLogger(__name__)


def download_starter_code(path: str):
    logger.info(f"Initializing project directory to '{path}'.")
    repo_owner = "flairis"
    repo_name = "ike-docs"
    subdirectory_path = f"{repo_name}-main/starter/"

    # URL to download the repository as a ZIP file
    zip_url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/heads/main.zip"

    response = requests.get(zip_url)
    if response.status_code == 200:
        # Open the ZIP file in memory
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            # Iterate over the files in the ZIP archive
            for file_name in zip_ref.namelist():
                # Check if the file belongs to the target subdirectory
                if file_name.startswith(subdirectory_path):
                    # Extract the file to the output directory
                    relative_path = file_name[
                        len(subdirectory_path) :
                    ]  # Remove subdir prefix
                    if not file_name.endswith("/"):  # Avoid empty names for directories
                        destination_path = os.path.join(path, relative_path)
                        if os.path.exists(destination_path):
                            logger.warning(f"File '{destination_path}' already exists.")
                            continue

                        # Ensure the destination directory exists
                        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                        # Write the file to the destination
                        with open(destination_path, "wb") as output_file:
                            output_file.write(zip_ref.read(file_name))
    else:
        logger.error(
            f"Failed to download ZIP file. HTTP Status code: {response.status_code}"
        )
        raise RuntimeError
