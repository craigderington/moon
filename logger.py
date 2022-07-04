LOGGING_CONFIG = { 
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": { 
        "standard": { 
            "format": "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
        },
        "default": {
            "format": "[%(asctime)s] %(levelname)s: %(lineno)d: %(message)s ",
        },
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s - %(funcName)s - %(thread)d - %(lineno)d: %(message)s ",
        },
    },
    "handlers": { 
        "console": { 
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
        "default": {
            "level": "DEBUG",
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": "moon.log"
        },
        "debug_file": {
            "level": "DEBUG",
            "formatter": "verbose",
            "class": "logging.FileHandler",
            "filename": "moon_debug.log"
        },
    },
    "loggers": { 
        "": { 
            "handlers": ["console", "default"],
            "level": "DEBUG",
            "propagate": False
        },
        "faucet": { 
            "handlers": ["console", "default"],
            "level": "INFO",
            "propagate": False
        },
        "__main__": { 
            "handlers": ["default", "console", "debug_file"],
            "level": "DEBUG",
            "propagate": False
        },
    } 
}
