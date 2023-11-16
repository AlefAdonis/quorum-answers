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
    bill_df = pd.read_csv(DATA_DIR+BILL_FILE, delimiter=",")
    legis_df = pd.read_csv(DATA_DIR+LEGIS_FILE, delimiter=",")
    results_vote_df = pd.read_csv(DATA_DIR+RESULTS_FILE, delimiter=",")
    votes_df = pd.read_csv(DATA_DIR+VOTE_FILE, delimiter=",")

    log.info("Answering the First Question")

    # renaming the id from the legis_df to match in the merge
    legis_df.rename({"id": "legislator_id"}, axis=1, inplace=True)
    bills_count = results_vote_df.merge(legis_df, on="legislator_id", how="left")

    # creating a copy of the legislator data to use the data without Data View problems
    result_of_legis_df = legis_df.copy()
    result_of_legis_df[["num_supported_bills", "num_opposed_bills"]] = 0
    for b in bills_count.itertuples():
        if b.vote_type == 1:
            if not result_of_legis_df.loc[result_of_legis_df["legislator_id"] == b.legislator_id, "num_supported_bills"].isnull().any():
                result_of_legis_df.loc[result_of_legis_df["legislator_id"] == b.legislator_id, "num_supported_bills"] += 1
            else:
                result_of_legis_df.loc[result_of_legis_df["legislator_id"] == b.legislator_id, "num_supported_bills"] = 1
            continue

        if b.vote_type == 2:
            if not result_of_legis_df.loc[result_of_legis_df["legislator_id"] == b.legislator_id, "num_opposed_bills"].isnull().any():
                result_of_legis_df.loc[result_of_legis_df["legislator_id"] == b.legislator_id, "num_opposed_bills"] += 1
            else:
                result_of_legis_df.loc[result_of_legis_df["legislator_id"] == b.legislator_id, "num_opposed_bills"] = 1

    result_of_legis_df.to_csv(DATA_DIR+COUNT_VOTES_LEGIS_FILE, sep=",", index=False)
    pass
