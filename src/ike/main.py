import typer
import importlib
import subprocess
import os
import zipfile
import requests
from io import BytesIO
from rich.status import Status

app = typer.Typer()

import logging
from rich.logging import RichHandler

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

    _download_starter_code("docs/")
    _install_node_modules("docs/")
    # _extract_definitions(...)  # TODO


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


def _install_node_modules(path: str):
    assert os.path.exists(path), f"Path '{path}' doesn't exist."

    package_json_path = os.path.join(path, "package.json")
    assert os.path.exists(package_json_path), f"No 'package.json' found in '{path}'."

    try:
        # Run npm install in the project directory
        logger.info(f"Installing dependencies to '{path}'.")
        with Status("[bold green]Installing dependencies..."):
            subprocess.run(
                ["npm", "install"],
                cwd=path,
                check=True,
                capture_output=True,
            )
        logger.info("Succesfully installed dependencies.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred while installing node modules: {e}")
        typer.Exit(1)
    except FileNotFoundError:
        logger.error("npm is not installed or not in PATH. Please install Node.js.")
        typer.Exit(1)


def _download_starter_code(path: str):
    repo_owner = "flairis"
    repo_name = "pyike"
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
                        # Ensure the destination directory exists
                        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                        # Write the file to the destination
                        with open(destination_path, "wb") as output_file:
                            output_file.write(zip_ref.read(file_name))
    else:
        print(f"Failed to download ZIP file. HTTP Status code: {response.status_code}")


def _extract_definitions(path: str):
    print("Extracting definitions...")


@app.command()
def dev():
    path = os.getcwd()
    try:
        # Run `npm run dev` in the project directory
        logger.info("Starting development server at http://localhost:3000")
        result = subprocess.run(
            ["npm", "run", "dev"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        if "Could not read package.json" in e.stderr:
            print("The current directory isn't a valid Ike project.")
            typer.Exit(1)
    except FileNotFoundError:
        print("npm is not installed or not in PATH. Please install Node.js.")
    except KeyboardInterrupt:
        logger.info("Development server stopped.")


@app.command()
def deploy():
    print("I fight for my friends")


def main():
    app()


if __name__ == "__main__":
    main()
