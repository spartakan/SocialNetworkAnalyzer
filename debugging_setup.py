import sys,os,platform,logging

logger = logging.getLogger(__name__)
def debug_print(message,debug = True):
    """
    Prints messages if the debug variable is set to true
    :param message: message to be printed
    :return: none
    """""
    if debug:
        print >> sys.stderr, "INFO: ", message
        print >> sys.stderr.flush()

def setup_logging():
    """
    Initializing the logging system used to write errors to a log file
    """
   #ceating a file handler
    #logger.level(logging.INFO)
    if platform.system() == 'Windows':
        LOG_FILE = os.path.expanduser("H:/twitterAnalyzer/CrawlingModule/Resources/error.log").replace("\\", "/")
    elif platform.system() == 'Linux':
        LOG_FILE = os.path.abspath(os.path.expanduser("~/twitterAnalyzer/CrawlingModule/Resources/error.log"))
    handler = logging.FileHandler(LOG_FILE)
    handler.setLevel(logging.ERROR)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    return logger
