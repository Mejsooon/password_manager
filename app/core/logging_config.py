import logging
import logging.config


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": (
                "%(asctime)s [%(levelname)s] "
                "%(name)s: %(message)s"
            ),
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },

        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "app.log",
            "encoding": "utf-8",
        },
    },

    "root": {
        "level": "WARNING",
        "handlers": ["console", "file"],
    },
}


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)