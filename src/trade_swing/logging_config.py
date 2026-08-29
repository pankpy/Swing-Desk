import logging
from pathlib import Path


def configure_logging(log_directory: str = "logs") -> None:
    """Configure console and rotating daily application logs once."""
    root = logging.getLogger()
    if root.handlers:
        return

    Path(log_directory).mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    file_handler = logging.FileHandler(Path(log_directory) / "scanner.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    root.setLevel(logging.INFO)
    root.addHandler(console)
    root.addHandler(file_handler)
