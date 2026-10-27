import logging.config


def setup_logging(level: str = "INFO") -> None:
    """Configure logging once for the whole app."""
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id": {"()": "app.request_context.RequestIdFilter"},
        },
        "formatters": {
            "default": {
                 "format": "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "filters": ["request_id"],
            },
        },
        "root": {
            "handlers": ["console"],
            "level": level,
        },
    })
