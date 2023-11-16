import logging
import datetime
import os

# File info for Input data
DATA_DIR = "./data/"
BILL_FILE = "bill.csv"
LEGIS_FILE = "legislators.csv"
VOTE_FILE = "votes.csv"
RESULTS_FILE = "vote_results.csv"

# File info for Output data
COUNT_VOTES_LEGIS_FILE = "legislators-support-oppose-count.csv"
RESULT_BILLS_FILE = "bill.csv"


def create_logger(log_path=".", log_level=logging.DEBUG):
    logger = logging.getLogger()
    logger.setLevel(log_level)

    path = os.path.normpath(log_path + "/Log/")
    if not os.path.isdir(path):
        os.mkdir(path)

    file_handler = logging.FileHandler(os.path.normpath(path + f"/{datetime.datetime.today().date()}.log"))

    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


if __name__ == "__main__":
    log = create_logger()

    log.info("Initiating Data Analysis")
    if (not os.path.isfile(DATA_DIR + BILL_FILE) or not os.path.isfile(DATA_DIR + LEGIS_FILE) or
            not os.path.isfile(DATA_DIR + VOTE_FILE) or not os.path.isfile(DATA_DIR + RESULTS_FILE)):
        log.error(f"There is input data missing! Please check the data dir {DATA_DIR} and rerun the script.")

    log.info("Extracting the data from csv files.")

