import json, time, logging

def read_instructions(file_path):
    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
            return file_contents
        
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return str(e)


def get_logger(name: str) -> logging.Logger:
    """
    Template for getting a logger.

    Args:
        name: Name of the logger.

    Returns: Logger.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)

    class TimingFilter(logging.Filter):
        """
        Custom logging filter to include the time in log records.
        """
        def filter(self, record: logging.LogRecord) -> bool:
            record.time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created))
            return True

    logger.addFilter(TimingFilter())
    return logger