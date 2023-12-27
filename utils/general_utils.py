import json, time, logging

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


def show_json(obj):
    display(json.loads(obj.model_dump_json()))

def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()