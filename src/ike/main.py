import importlib
import json
import keyring
import logging
import os
import pathspec
import shutil
import subprocess
import zipfile
from io import BytesIO
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import requests
import typer
from rich.prompt import Prompt
from rich.status import Status
from ike.extract import extract_definitions, write_definition

app = typer.Typer()
logger = logging.getLogger(__name__)


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
    _link_pages(project_root)


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


def _link_pages(project_root: str):
    for root, _, files in os.walk(project_root):
        for file in files:
            relative_path = Path(os.path.join(root, file)).relative_to(project_root)
            if str(relative_path).startswith(".ike") or not file.endswith(".md"):
                continue
            _link_page(project_root, str(relative_path))

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


def _get_project_root():
    project_root = os.getcwd() 

    if not os.path.exists(os.path.join(project_root, "ike.yaml")): 
        logger.error("The current directory isn't a valid Ike project.") 
        raise typer.Exit(1) 

    return project_root


@app.command()
def dev():
    project_root = _get_project_root()

    try:
        # TODO: Load package name from ike.yaml
        package = importlib.import_module("rich")
    except ImportError:
        # TODO: Raise helpful error.
        raise

    node_root = _get_node_root(project_root)
    for definition in extract_definitions(package):
        write_definition(definition, os.path.join(node_root, "public", "api"))

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
    api_key = keyring.get_password('ike', 'api_key')

    if not api_key:
        api_key = typer.prompt("Enter API key", hide_input=True)
        keyring.set_password('ike', 'api_key', api_key)

    project_root = _get_project_root()
    node_root = _get_node_root(project_root)
    build_path = os.path.join(node_root, "build.zip")
    
    logger.info("Queueing deployment...")
    _build_project(node_root, build_path)
    _submit_deployment(api_key, build_path)

    # Clean up build artifact
    if os.path.exists(build_path):
        os.remove(build_path)

    
def _build_project(node_root: str, build_path: str):
    with open(".gitignore", "r") as file:
        ignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", file)

    with zipfile.ZipFile(build_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(node_root):  
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, node_root)
                
                if not ignore_spec.match_file(rel_path):
                    zipf.write(file_path, rel_path)


def _submit_deployment(api_key: str, build_path: str) -> str:
    with open(build_path, "rb") as file:
        response = requests.post("https://yron03hrwk.execute-api.us-east-1.amazonaws.com/dev/docs/build", 
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/zip"
            }, 
            data=file
        )

    if response.status_code == 202:
        url = json.loads(response.text)["body"]
        logger.info(f"Deployment queued, will be available at {url}")
    else:
        logger.info(f"Deployment failed: {response.status_code} {response.text}")
        raise typer.Exit(1)
    

def main():
    app()


if __name__ == "__main__":
    main()
