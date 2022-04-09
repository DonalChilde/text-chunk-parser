# """App config values


# """
# import logging
# import os
# from logging.handlers import RotatingFileHandler
# from pathlib import Path
# from typing import Union, Optional

# import click

# NAMESPACE = "pfmsoft"
# PROJECT_SLUG = "text_chunk_parser"
# PROJECT_NAME = "text-chunk-parser"


# class App_Config:
#     """Store App configuration values here.

#     Loads env variables, with usable defaults.
#     If used, set env variables - maybe using dotenv - before
#     instancing App_Config.
#     """

#     APP_NAME = os.getenv(
#         f"{NAMESPACE}{PROJECT_SLUG}_APP_NAME",
#         f"{ PROJECT_NAME.replace(' ','-') }",
#     )
#     """The name of the app. Should be namespaced to prevent collision."""

#     APP_DIR = os.getenv(
#         f"{NAMESPACE}{PROJECT_SLUG}_APP_DIR",
#         click.get_app_dir(APP_NAME, force_posix=True),
#     )
#     """The app data directory. Location is system dependent."""

#     LOG_LEVEL = int(
#         os.getenv(
#             f"{NAMESPACE}{PROJECT_SLUG}_LOG_LEVEL",
#             str(logging.WARNING),
#         )
#     )
#     """App wide setting for log level"""
#     LOG_DIR = os.getenv(
#         f"{NAMESPACE}{PROJECT_SLUG}_LOG_PATH", str(Path("{APP_DIR}") / "logs")
#     )


# def log_file_handler(
#     file_path: Path,
#     log_level: int = logging.WARNING,
#     format_string: Optional[str] = None,
# ):
#     handler = RotatingFileHandler(file_path, maxBytes=102400, backupCount=10)
#     if format_string is None:
#         format_string = (
#             "%(asctime)s %(levelname)s:%(funcName)s: "
#             "%(message)s [in %(pathname)s:%(lineno)d]"
#         )
#     handler.setFormatter(logging.Formatter(format_string))
#     handler.setLevel(log_level)
#     return handler


# def file_logger(
#     log_dir: str, logger_name: str, log_level: Union[str, int]
# ) -> logging.Logger:
#     """Configure a logger with a RotatingFileHandler."""
#     log_file_name = f"{logger_name}.log"
#     logger_ = logging.getLogger(logger_name)
#     log_dir_path: Path = Path(log_dir)
#     log_dir_path.mkdir(parents=True, exist_ok=True)
#     log_file_path = log_dir_path / Path(log_file_name)
#     handler = log_file_handler(log_file_path, log_level=log_level)
#     logger_.addHandler(handler)
#     logger_.setLevel(log_level)
#     ############################################################
#     # NOTE add file handler to other library modules as needed #
#     ############################################################
#     # async_logger = logging.getLogger("eve_esi_jobs")
#     # async_logger.addHandler(file_handler)
#     # async_logger.setLevel(log_level)
#     logger_.info("Rotating File Logger initializd at %s", log_file_path)
#     return logger_
