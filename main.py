import logging
import datetime
import os
import numpy as np
import pandas as pd

# File info for Input data
DATA_DIR = "./data/"
BILL_FILE = "bill.csv"
LEGIS_FILE = "legislators.csv"
VOTE_FILE = "votes.csv"
RESULTS_FILE = "vote_results.csv"

# File info for Output data
COUNT_VOTES_LEGIS_FILE = "legislators-support-oppose-count.csv"
RESULT_BILLS_FILE = "bills.csv"


def create_logger(log_path=".", log_level=logging.DEBUG):
    """
    Creates a global log
    :param log_path: path where the log will be stored
    :param log_level: level of the log (DEBUG, ERROR, WARNING, ...)
    :return: logger object
    """

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
    if (not os.path.isfile(os.path.normpath(DATA_DIR + BILL_FILE)) or not os.path.isfile(os.path.normpath(DATA_DIR + LEGIS_FILE)) or
            not os.path.isfile(os.path.normpath(DATA_DIR + VOTE_FILE)) or not os.path.isfile(os.path.normpath(DATA_DIR + RESULTS_FILE))):
        log.error(f"There is input data missing! Please check the data dir {DATA_DIR} and rerun the script.")

    log.info("Extracting the data from csv files.")
    bill_df = pd.read_csv(os.path.normpath(DATA_DIR+BILL_FILE), delimiter=",")
    legis_df = pd.read_csv(os.path.normpath(DATA_DIR+LEGIS_FILE), delimiter=",")
    results_vote_df = pd.read_csv(os.path.normpath(DATA_DIR+RESULTS_FILE), delimiter=",")
    votes_df = pd.read_csv(os.path.normpath(DATA_DIR+VOTE_FILE), delimiter=",")

    log.info("Answering the First Question")
    # creating a copy of the legislator data to use the data without Data View problems
    result_of_legis_df = legis_df.copy()
    result_of_legis_df[["num_supported_bills", "num_opposed_bills"]] = 0
    for b in results_vote_df.itertuples():
        if b.vote_type == 1:
            result_of_legis_df.loc[result_of_legis_df["id"] == b.legislator_id, "num_supported_bills"] += 1

        if b.vote_type == 2:
            result_of_legis_df.loc[result_of_legis_df["id"] == b.legislator_id, "num_opposed_bills"] += 1

    log.info("Creating the Output File for the first question.")
    result_of_legis_df.to_csv(os.path.normpath(DATA_DIR+COUNT_VOTES_LEGIS_FILE), sep=",", index=False)

    log.info("Answering the second question")
    # Merging the two dataframes
    bills_vote_df = results_vote_df.merge(votes_df, left_on="vote_id", right_on="id", how="left",
                                          suffixes=[None, "_vote"])

    # Processing the count of number of votes for each bill
    bills_result_df = bill_df.copy()
    bills_result_df[["supporter_count", "opposer_count"]] = 0
    for v in bills_vote_df.itertuples():
        if v.vote_type == 1:
            bills_result_df.loc[bills_result_df["id"] == v.bill_id, "supporter_count"] += 1

        if v.vote_type == 2:
            bills_result_df.loc[bills_result_df["id"] == v.bill_id, "opposer_count"] += 1

    # Getting the name of the Sponsor
    bills_result_final_df = bills_result_df.merge(legis_df, how="left", left_on="sponsor_id", right_on="id",
                                                  suffixes=[None, "_legislator"])

    # Sanitizing the data results
    bills_result_final_df.drop(["sponsor_id", "id_legislator"], axis=1, inplace=True)
    bills_result_final_df.rename({"name": "primary_sponsor"}, axis=1, inplace=True)

    bills_result_final_df["primary_sponsor"].fillna("Unknown", inplace=True)

    columns = ["id", "title", "supporter_count", "opposer_count", "primary_sponsor"]
    bills_result_final_df = bills_result_final_df[columns]

    log.info("Creating the Output File for the second question.")
    bills_result_final_df.to_csv(os.path.normpath(DATA_DIR+ RESULT_BILLS_FILE), sep=",", index=False)

    log.info("Finishing process!")
