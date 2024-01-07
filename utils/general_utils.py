import logging
import time

def read_instructions(file_path):
    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
            return file_contents
        
    except FileNotFoundError:
        return None
    
    except Exception as e:
        return None


def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Enhanced template for getting a logger.

    Args:
        name (str): Name of the logger.
        level: Logging level, defaults to logging.INFO.

    Returns:
        logging.Logger: Configured logger.
    """

    # Set up a specific format for log messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a StreamHandler (you can also add FileHandler if needed)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)

    # Initialize the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple handlers if the logger is already initialized
    if not logger.handlers:
        logger.addHandler(stream_handler)

    class TimingFilter(logging.Filter):
        """
        Custom logging filter to include the time in log records.
        """
        def filter(self, record: logging.LogRecord) -> bool:
            record.time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created))
            return True

    # Add the custom timing filter to the logger
    logger.addFilter(TimingFilter())

    return logger