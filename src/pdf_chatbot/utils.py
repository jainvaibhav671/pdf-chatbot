from fastapi import UploadFile
import nanoid
import os
import logging

from pdf_chatbot.constants import PUBLIC_FOLDER, LOGS

def save_file(file: UploadFile) -> str:
    """
    Save the file to the public folder with a unique name
    and return the path
    """

    file_name = file.filename

    file_name = f"{nanoid.generate(size=4)}-{file_name}".replace(" ", "-")
    file_path = os.path.join(PUBLIC_FOLDER, file_name)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return file_path

def get_logger(name: str):
    """
    Get a logger with the given name
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger

def log(logger: logging.Logger, *message: str, level: str = "debug"):

    """
    Log a message with a given level if logs are enabled
    """

    if not LOGS:
        return

    if level == "debug":
        logger.debug(" ".join(message))
    elif level == "info":
        logger.info(" ".join(message))
    elif level == "warning":
        logger.warning(" ".join(message))
    elif level == "error":
        logger.error(" ".join(message))

def generate_session_id() -> str:
    """
    Generate a unique session ID
    """

    return nanoid.generate(size=8)

