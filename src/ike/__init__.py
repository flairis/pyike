import logging
from rich.logging import RichHandler

logger = logging.getLogger(__name__)

def setup_logging(level: int = logging.DEBUG) -> None:
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
