import importlib
import logging
import os
import subprocess
import zipfile
from io import BytesIO
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import requests
import typer
from rich.logging import RichHandler
from rich.prompt import Prompt
from rich.status import Status

app = typer.Typer()
logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    # Taken from https://github.com/fastapi/fastapi-cli/blob/main/src/fastapi_cli/logging.py#L8
    rich_handler = RichHandler(
        show_time=False,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,
        show_path=False,
    )
    rich_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(rich_handler)

    logger.setLevel(level)
    logger.propagate = False


setup_logging()


@app.command()
def init():
    if not _is_node_installed():
        logger.error(
            "Ike depends on Node.js. Make sure it's installed in the current "
            "environment and available in the PATH."
        )
        raise typer.Exit(1)

    package_name = typer.prompt("What's the name of your package?")

    try:
        importlib.import_module(package_name)
    except ImportError:
        logger.error(
            f"Ike couldn't import a package named '{package_name}'. Make sure it's "
            "installed in the current environment."
        )
        raise typer.Exit(1)

    project_root = os.path.join(os.getcwd(), "docs/")
    _download_starter_code(project_root)
    _install_node_modules(project_root)
    _link_config_file(project_root)

    # _extract_definitions(...)  # TODO


def _watch_for_new_pages(project_root: str):
    event_handler = FileLinker(project_root)
    observer = Observer()
    observer.daemon = True
    observer.schedule(event_handler, path=project_root, recursive=True)
    observer.start()


def _link_config_file(project_root: str):
    src = os.path.join(project_root, "ike.yaml")
    dst = os.path.join(_get_node_root(project_root), "public", "ike.yaml")

    if os.path.exists(dst): 
        logger.warning(f"Overwriting old copy of config '{dst}'.")
        os.remove(dst)

    logger.debug(f"Linking config file from '{src}' to '{dst}'")
    os.link(src, dst)


def _link_page(project_root: str, relative_path: str):
    src = os.path.join(project_root, relative_path)
    dst = os.path.join(_get_node_root(project_root), "pages", relative_path)

    if os.path.exists(dst):
        logger.warning(f"Overwriting old copy of page '{dst}'.")
        os.remove(dst)
        
    logger.debug(f"Linking page from '{src}' to '{dst}'")
    os.link(src, dst)


# Define a custom event handler
class FileLinker(FileSystemEventHandler):

    def __init__(self, project_root: str):
        self._project_root = Path(project_root)
    
    def on_created(self, event):
        if not event.is_directory:
            relative_path = Path(event.src_path).relative_to(self._project_root)
            if str(relative_path).startswith(".ike") or not str(relative_path).endswith(".md"):
                return
            _link_page(self._project_root, relative_path)


def _is_node_installed() -> bool:
    try:
        result = subprocess.run(
            ["node", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            return True
        else:
            return False
    except FileNotFoundError:
        return False


def _install_node_modules(project_root: str):
    node_root = _get_node_root(project_root)
    assert os.path.exists(node_root), f"Path '{node_root}' doesn't exist."

    package_json_path = os.path.join(node_root, "package.json")
    assert os.path.exists(package_json_path), f"No 'package.json' found in '{node_root}'."

    try:
        # Run npm install in the project directory
        with Status("[bold green]Installing dependencies..."):
            subprocess.run(
                ["npm", "install"],
                cwd=node_root,
                check=True,
                capture_output=True,
            )
        logger.info("Succesfully installed dependencies.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred while installing node modules: {e}")
        raise typer.Exit(1)
    except FileNotFoundError:
        logger.error("npm is not installed or not in PATH. Please install Node.js.")
        raise typer.Exit(1)


def _download_starter_code(path: str):
    logger.info(f"Initializing project directory to '{path}'.")
    repo_owner = "flairis"
    repo_name = "ike-docs"
    subdirectory_path = f"{repo_name}-main/starter/"

    # URL to download the repository as a ZIP file
    zip_url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/heads/main.zip"

    response = requests.get(zip_url)
    if response.status_code == 200:
        # Open the ZIP file in memory
        with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
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
        logger.error(f"Failed to download ZIP file. HTTP Status code: {response.status_code}")
        raise typer.Exit(1)


def _get_node_root(project_root: str) -> str:
    return os.path.join(project_root, ".ike")

def _extract_definitions(path: str):
    print("Extracting definitions...")


@app.command()
def dev():
    project_root = os.getcwd()
    if not os.path.exists(os.path.join(project_root, "ike.yaml")):
        logger.error("The current directory isn't a valid Ike project.")
        raise typer.Exit(1)

    node_root = _get_node_root(project_root)
    _watch_for_new_pages(project_root)
    try:
        # Run `npm run dev` in the project directory
        logger.info("Starting development server at http://localhost:3000")
        subprocess.run(
            ["npm", "run", "dev"],
            check=True,
            capture_output=True,
            text=True,
            cwd=node_root
        )
    except subprocess.CalledProcessError as e:
        if "Could not read package.json" in e.stderr:
            raise typer.Exit(1)
    except FileNotFoundError:
        logger.error("npm is not installed or not in PATH. Please install Node.js.")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        logger.info("Development server stopped.")


@app.command()
def deploy():
    print("I fight for my friends")


def main():
    app()


if __name__ == "__main__":
    main()
