import json
import logging

# help.set_logging(stream=True, fileh=True, filename=log_file)

def set_logging(stream=False, fileh=False, filename="example.log"):
    """set basic logging configurations (root logger).
    args:
        stream (bool): whether logging.info log to console.
        fileh (bool): whether write log to file.
        filename (str): the path of log file.
    return:
        configued root logger.
    """
    handlers = []
    level = logging.INFO
    log_format = '%(asctime)s: %(message)s'

    if stream:
        handlers.append(logging.StreamHandler())
    if fileh:
        handlers.append(logging.FileHandler(filename))
    logging.basicConfig(format=log_format, handlers=handlers, level=level)
    return logging.getLogger()

def read_json(filename):
    if os.path.isfile(filename):
        logging.info("reading from json file: " + filename)
        with open(filename) as data_file:
            data = json.load(data_file)
        logging.info("finish reading json file")
        return data
    else:
        raise FileNotFoundError("json file: ", filename)


def write_json(filename, data):
    logging.info("writing dmoz to " + str(filename))
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    logging.info("finish writing to " + str(filename))