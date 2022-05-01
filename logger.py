import logging


logging.basicConfig(filename='logfile_hitler_wiki.log',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.ERROR)
logger = logging.getLogger("hitler_wiki")
