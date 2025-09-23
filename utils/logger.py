import logging
import pathlib

from logging.handlers import RotatingFileHandler


def define_logger(name:str,log_file:str=None)->logging.Logger:
    """
        log handler for console and file logs
    """
    # create the logger
    logger=logging.getLogger(name)
    #set the logger level
    logger.setLevel(logging.INFO)
    #Create  file handler and set level
    file_handler=logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    #create console handler and set level
    console_handler=logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    #Create console handler and set level
    #Create log formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    #console formatter
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    #add formatters to handlers
    #file formatter
    file_handler.setFormatter(file_formatter)
    #console formatter
    console_handler.setFormatter(console_formatter)
    #add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    #return the logger
    return logger


