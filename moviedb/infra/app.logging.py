import logging

from flask import Flask


def configure_logging(logging_level: int = logging.DEBUG,
                      enable_http_log: bool = False) -> None:

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging_level)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))