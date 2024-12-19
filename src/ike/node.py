import logging
import os
import subprocess

from rich.status import Status

logger = logging.getLogger(__name__)


def get_node_root(project_root: str) -> str:
    return os.path.join(project_root, ".ike")


def is_node_installed() -> bool:
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


def install_node_modules(project_root: str):
    node_root = get_node_root(project_root)
    assert os.path.exists(node_root), f"Path '{node_root}' doesn't exist."

    package_json_path = os.path.join(node_root, "package.json")
    assert os.path.exists(
        package_json_path
    ), f"No 'package.json' found in '{node_root}'."

    try:
        with Status("[bold green]Installing dependencies..."):
            subprocess.run(
                ["npm", "install"],
                cwd=node_root,
                check=True,
                capture_output=True,
            )
        logger.info("Succesfully installed dependencies.")
    except subprocess.CalledProcessError:
        logger.error("Error occurred while installing node modules")
        raise


def run_node_dev(project_root: str):
    node_root = get_node_root(project_root)
    try:
        # TODO: Use the actual port instead of hardcoding it.
        logger.info("Starting development server at http://localhost:3000")
        subprocess.run(
            ["npm", "run", "dev"],
            check=True,
            capture_output=True,
            text=True,
            cwd=node_root,
        )
    except KeyboardInterrupt:
        logger.info("Development server stopped.")
