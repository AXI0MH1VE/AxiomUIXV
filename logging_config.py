import logging
import logging.config
from pathlib import Path
from typing import Dict


def configure_logging(run_id: str, log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    fmt = "%(asctime)s [%(levelname)s] [%(threadName)s] %(name)s - %(message)s"

    config: Dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": fmt},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
            },
            "orchestrator_file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "standard",
                "filename": str(log_dir / f"orchestrator-{run_id}.log"),
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "orchestrator": {
                "level": "DEBUG",
                "handlers": ["console", "orchestrator_file"],
                "propagate": False,
            },
            "agent": {
                "level": "DEBUG",
                "handlers": ["console", "orchestrator_file"],
                "propagate": False,
            },
            "ollama": {
                "level": "DEBUG",
                "handlers": ["console", "orchestrator_file"],
                "propagate": False,
            },
            "tools": {
                "level": "DEBUG",
                "handlers": ["console", "orchestrator_file"],
                "propagate": False,
            },
        },
        "root": {
            "level": "WARNING",
            "handlers": ["console"],
        },
    }

    logging.config.dictConfig(config)
