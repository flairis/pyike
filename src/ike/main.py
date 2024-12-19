import importlib
import logging
import os

import typer

from .bootstrap import download_starter_code
from .link import link_config_file, link_existing_pages, link_page_on_creation
from .node import install_node_modules, is_node_installed, run_node_dev
from .parser import prepare_references

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.command()
def init():
    if not is_node_installed():
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
    download_starter_code(project_root)
    install_node_modules(project_root)
    link_config_file(project_root)
    link_existing_pages(project_root)


@app.command()
def dev():
    project_root = os.getcwd()
    if not os.path.exists(os.path.join(project_root, "ike.yaml")):
        logger.error("The current directory isn't a valid Ike project.")
        raise typer.Exit(1)

    prepare_references(project_root)
    link_config_file(project_root)
    link_existing_pages(project_root)
    link_page_on_creation(project_root)
    run_node_dev(project_root)


@app.command()
def deploy():
    print("I fight for my friends")


def main():
    app()


if __name__ == "__main__":
    main()
